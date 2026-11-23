"""Source-bound workflow commands and durable state transitions for F02-STATE."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from uuid import uuid4

from backend.core.schemas.models import Identifier, Scope, Sha256
from backend.storage.database import state_write
from backend.storage.state_schema import (
    approvals,
    attempts,
    events,
    jobs,
    mutations,
    runs,
    versions,
)
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import Connection, Engine, select
from sqlalchemy.dialects.sqlite import insert


class WorkflowError(ValueError):
    """A safe, actionable rejection of a workflow command."""


class InvalidCommand(WorkflowError):
    pass


class RecordConflict(WorkflowError):
    pass


class DuplicateMutation(RecordConflict):
    pass


class InvalidTransition(RecordConflict):
    pass


class State(StrEnum):
    UPLOADED = "UPLOADED"
    BASELINE_CREATED = "BASELINE_CREATED"
    LANGUAGE_ROUTED = "LANGUAGE_ROUTED"
    ANALYZING = "ANALYZING"
    FINDINGS_READY = "FINDINGS_READY"
    AWAITING_ISSUE_SELECTION = "AWAITING_ISSUE_SELECTION"
    REFACTORING = "REFACTORING"
    VALIDATING_CANDIDATES = "VALIDATING_CANDIDATES"
    AWAITING_PATCH_APPROVAL = "AWAITING_PATCH_APPROVAL"
    COMBINED_VALIDATION = "COMBINED_VALIDATION"
    FINALIZED = "FINALIZED"
    REPORT_READY = "REPORT_READY"
    BLOCKED_INPUT = "BLOCKED_INPUT"
    BASELINE_FAILURE = "BASELINE_FAILURE"
    UNVERIFIED = "UNVERIFIED"
    PATCH_FAILED = "PATCH_FAILED"
    MERGE_CONFLICT = "MERGE_CONFLICT"
    USER_CANCELLED = "USER_CANCELLED"


class Gate(StrEnum):
    ISSUE_SELECTION = "ISSUE_SELECTION"
    PATCH_APPROVAL = "PATCH_APPROVAL"


_APPROVAL_TRANSITIONS = {
    Gate.ISSUE_SELECTION: (State.AWAITING_ISSUE_SELECTION, State.REFACTORING),
    Gate.PATCH_APPROVAL: (State.AWAITING_PATCH_APPROVAL, State.COMBINED_VALIDATION),
}
_NEXT = {
    State.UPLOADED: {State.BASELINE_CREATED, State.BLOCKED_INPUT},
    State.BASELINE_CREATED: {State.LANGUAGE_ROUTED, State.BLOCKED_INPUT},
    State.LANGUAGE_ROUTED: {State.ANALYZING, State.UNVERIFIED},
    State.ANALYZING: {State.FINDINGS_READY, State.BASELINE_FAILURE, State.UNVERIFIED},
    State.FINDINGS_READY: {State.AWAITING_ISSUE_SELECTION},
    State.AWAITING_ISSUE_SELECTION: set(),
    State.REFACTORING: {State.VALIDATING_CANDIDATES, State.PATCH_FAILED, State.UNVERIFIED},
    State.VALIDATING_CANDIDATES: {
        State.AWAITING_PATCH_APPROVAL,
        State.PATCH_FAILED,
        State.UNVERIFIED,
    },
    State.AWAITING_PATCH_APPROVAL: set(),
    State.COMBINED_VALIDATION: {State.FINALIZED, State.MERGE_CONFLICT, State.UNVERIFIED},
    State.FINALIZED: {State.REPORT_READY},
}
_IDENTIFIER = TypeAdapter(Identifier)
_SHA256 = TypeAdapter(Sha256)


def _validate_id(value: str, entity: str) -> None:
    try:
        _IDENTIFIER.validate_python(value, strict=True)
    except ValidationError:
        raise InvalidCommand(f"Invalid {entity} identifier.") from None
    if not value.startswith(f"{entity}:"):
        raise InvalidCommand(f"Invalid {entity} identifier.")


def _validate_hash(value: str) -> None:
    try:
        _SHA256.validate_python(value, strict=True)
    except ValidationError:
        raise InvalidCommand("Invalid SHA-256 fingerprint.") from None


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class Mutation:
    """POST context. The actor comes from the trusted caller's authentication layer."""

    actor_id: str
    idempotency_key: str = field(repr=False)

    def __post_init__(self) -> None:
        _validate_id(self.actor_id, "actor")
        if (
            not isinstance(self.idempotency_key, str)
            or not 1 <= len(self.idempotency_key) <= 128
            or any(not 33 <= ord(character) <= 126 for character in self.idempotency_key)
        ):
            raise InvalidCommand("Invalid idempotency key.")


def _record_mutation(
    connection: Connection,
    mutation: Mutation,
    operation: str,
    target_id: str,
    now: str,
) -> None:
    result = connection.execute(
        insert(mutations)
        .values(
            actor_id=mutation.actor_id,
            operation=operation,
            target_id=target_id,
            key_sha256=sha256(mutation.idempotency_key.encode("ascii")).hexdigest(),
            created_at=now,
        )
        .on_conflict_do_nothing()
    )
    if result.rowcount != 1:
        raise DuplicateMutation("This mutation was already applied.")


def _run_state(connection: Connection, run_id: str) -> State:
    _validate_id(run_id, "run")
    value = connection.scalar(select(runs.c.state).where(runs.c.id == run_id))
    if value is None:
        raise InvalidCommand("Run does not exist.")
    return State(value)


def _check_transition(source: State, target: State) -> None:
    if target in _NEXT.get(source, ()):
        return
    if target == State.USER_CANCELLED and source in _NEXT and source != State.FINALIZED:
        return
    raise InvalidTransition("The requested state transition is not allowed.")


def _apply_transition(
    connection: Connection,
    run_id: str,
    source: State | None,
    target: State,
    actor_id: str,
    now: str,
    *,
    job_id: str | None = None,
) -> None:
    connection.execute(runs.update().where(runs.c.id == run_id).values(state=target))
    connection.execute(
        events.insert().values(
            run_id=run_id,
            source_state=source,
            target_state=target,
            actor_id=actor_id,
            created_at=now,
            job_id=job_id,
        )
    )


class Workflow:
    """Transaction boundary for metadata writes. Callers supply authorized inputs."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def register_version(
        self,
        project_id: str,
        version_id: str,
        v0_id: str,
        manifest_sha256: str,
        mutation: Mutation,
    ) -> None:
        _validate_id(project_id, "project")
        _validate_id(version_id, "version")
        _validate_id(v0_id, "version")
        _validate_hash(manifest_sha256)
        with state_write(self.engine) as connection:
            now = utc_now()
            _record_mutation(connection, mutation, "register_version", project_id, now)
            if version_id != v0_id and not connection.scalar(
                select(versions.c.id).where(
                    versions.c.id == v0_id,
                    versions.c.v0_id == v0_id,
                    versions.c.project_id == project_id,
                )
            ):
                raise InvalidCommand("Version does not reference the project's original snapshot.")
            result = connection.execute(
                insert(versions)
                .values(
                    id=version_id,
                    project_id=project_id,
                    v0_id=v0_id,
                    manifest_sha256=manifest_sha256,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            if result.rowcount != 1:
                raise RecordConflict("Version already exists.")

    def create_run(self, scope: Scope, mutation: Mutation) -> None:
        with state_write(self.engine) as connection:
            now = utc_now()
            _record_mutation(connection, mutation, "create_run", scope.project_id, now)
            baseline = connection.scalar(
                select(versions.c.manifest_sha256).where(
                    versions.c.id == scope.version_id,
                    versions.c.v0_id == scope.version_id,
                    versions.c.project_id == scope.project_id,
                )
            )
            if baseline is None or baseline != scope.baseline_sha256:
                raise InvalidCommand("Run does not reference the project's original snapshot.")
            result = connection.execute(
                insert(runs)
                .values(
                    id=scope.run_id,
                    analysis_id=scope.analysis_id,
                    v0_id=scope.version_id,
                    source_revision=scope.source_revision,
                    state=State.UPLOADED,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            if result.rowcount != 1:
                raise RecordConflict("Run or analysis identifier already exists.")
            connection.execute(
                events.insert().values(
                    run_id=scope.run_id,
                    target_state=State.UPLOADED,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
            )

    def transition(self, run_id: str, expected: State, target: State, mutation: Mutation) -> None:
        with state_write(self.engine) as connection:
            now = utc_now()
            source = _run_state(connection, run_id)
            _record_mutation(connection, mutation, "transition", run_id, now)
            if source != expected:
                raise InvalidTransition("The run has moved from the expected state.")
            _check_transition(source, target)
            _apply_transition(connection, run_id, source, target, mutation.actor_id, now)
            self._supersede_pending(connection, run_id, now)

    def record_approval(
        self,
        run_id: str,
        gate: Gate,
        approval_id: str,
        fingerprint: str,
        mutation: Mutation,
    ) -> None:
        _validate_id(approval_id, "approval")
        _validate_hash(fingerprint)
        if not isinstance(gate, Gate):
            raise InvalidCommand("Unknown approval gate.")
        expected, target = _APPROVAL_TRANSITIONS[gate]
        with state_write(self.engine) as connection:
            now = utc_now()
            source = _run_state(connection, run_id)
            _record_mutation(connection, mutation, gate.value, run_id, now)
            if source != expected:
                raise InvalidTransition("The run is not awaiting this approval.")
            result = connection.execute(
                insert(approvals)
                .values(
                    id=approval_id,
                    run_id=run_id,
                    gate=gate,
                    fingerprint=fingerprint,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            if result.rowcount != 1:
                raise RecordConflict("Approval already exists.")
            _apply_transition(connection, run_id, source, target, mutation.actor_id, now)
            self._supersede_pending(connection, run_id, now)

    def record_attempt(self, run_id: str, attempt_id: str, mutation: Mutation) -> None:
        _validate_id(attempt_id, "attempt")
        with state_write(self.engine) as connection:
            now = utc_now()
            source = _run_state(connection, run_id)
            _record_mutation(connection, mutation, "record_attempt", run_id, now)
            if source not in (State.REFACTORING, State.VALIDATING_CANDIDATES):
                raise InvalidTransition("The current state does not accept attempts.")
            result = connection.execute(
                insert(attempts)
                .values(
                    id=attempt_id,
                    run_id=run_id,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            if result.rowcount != 1:
                raise RecordConflict("Attempt already exists.")

    def enqueue_transition(
        self,
        run_id: str,
        expected: State,
        target: State,
        mutation: Mutation,
    ) -> str:
        """Commit a pending job and its idempotency key before contacting Redis."""
        with state_write(self.engine) as connection:
            now = utc_now()
            source = _run_state(connection, run_id)
            _record_mutation(connection, mutation, "enqueue_transition", run_id, now)
            if source != expected:
                raise InvalidTransition("The run has moved from the expected state.")
            _check_transition(source, target)
            if target == State.USER_CANCELLED:
                raise InvalidTransition("Cancellation must be applied directly.")
            job_id = f"job:{uuid4().hex}"
            result = connection.execute(
                insert(jobs)
                .values(
                    id=job_id,
                    run_id=run_id,
                    source_state=source,
                    target_state=target,
                    status="QUEUED",
                    dispatch_after=now,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            if result.rowcount != 1:
                raise RecordConflict("A job is already registered for this run state.")
            return job_id

    def complete_job(self, job_id: str) -> bool:
        """Apply a queued transition once, even with concurrent or replayed delivery."""
        _validate_id(job_id, "job")
        with state_write(self.engine) as connection:
            job = connection.execute(select(jobs).where(jobs.c.id == job_id)).one_or_none()
            if job is None or job.status != "QUEUED":
                return False
            now = utc_now()
            source = _run_state(connection, job.run_id)
            if source != job.source_state:
                connection.execute(
                    jobs.update()
                    .where(jobs.c.id == job_id)
                    .values(
                        status="SUPERSEDED",
                        finished_at=now,
                    )
                )
                return False
            target = State(job.target_state)
            _check_transition(source, target)
            _apply_transition(
                connection, job.run_id, source, target, job.actor_id, now, job_id=job_id
            )
            connection.execute(
                jobs.update()
                .where(jobs.c.id == job_id)
                .values(
                    status="COMPLETED",
                    finished_at=now,
                )
            )
            return True

    @staticmethod
    def _supersede_pending(connection: Connection, run_id: str, now: str) -> None:
        connection.execute(
            jobs.update()
            .where(jobs.c.run_id == run_id, jobs.c.status == "QUEUED")
            .values(status="SUPERSEDED", finished_at=now)
        )
