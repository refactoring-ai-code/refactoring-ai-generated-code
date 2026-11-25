"""Exercise persisted workflow behavior through its command and POST boundaries."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from backend.core.schemas.models import ErrorEnvelope, Scope, utc_timestamp
from backend.core.workflow import (
    DuplicateMutation,
    Gate,
    InvalidCommand,
    InvalidTransition,
    Mutation,
    RecordConflict,
    State,
    Workflow,
    WorkflowError,
)
from backend.core.workflow_http import post_mutation, workflow_error_response
from backend.storage.database import migrate_state, state_engine
from backend.storage.state_schema import (
    approvals,
    attempts,
    events,
    jobs,
    mutations,
    runs,
    versions,
)
from backend.workers.state_queue import REDELIVERY_SECONDS, dispatch_pending
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import inspect, select

BASELINE = "a" * 64
SCOPE = Scope(
    project_id="project:fixture",
    version_id="version:original",
    analysis_id="analysis:one",
    run_id="run:one",
    source_revision="b" * 40,
    baseline_sha256=BASELINE,
)


@pytest.fixture
def workflow(tmp_path):
    engine = state_engine(tmp_path / "state.db")
    migrate_state(engine)
    yield Workflow(engine)
    engine.dispose()


def mutation(key):
    return Mutation("actor:fixture", key)


def add_run(workflow):
    workflow.register_version(
        SCOPE.project_id, SCOPE.version_id, SCOPE.version_id, BASELINE, mutation("register")
    )
    workflow.create_run(SCOPE, mutation("create"))


def rows(workflow, table):
    with workflow.engine.connect() as connection:
        return connection.execute(select(table)).all()


def test_migration_repeated_on_new_and_existing_database(tmp_path):
    for filename, existing in (("new.db", False), ("existing.db", True)):
        database = tmp_path / filename
        if existing:
            with closing(sqlite3.connect(database)) as connection, connection:
                connection.execute("CREATE TABLE existing_records (name TEXT)")
                connection.execute("INSERT INTO existing_records VALUES ('preserved')")
                connection.execute("CREATE TABLE alembic_version (version_num TEXT)")
                connection.execute("INSERT INTO alembic_version VALUES ('unrelated')")
        engine = state_engine(database)
        try:
            migrate_state(engine)
            migrate_state(engine)
            assert "genesis_runs" in inspect(engine).get_table_names()
            with engine.connect() as connection:
                assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
                assert (
                    connection.exec_driver_sql(
                        "SELECT version_num FROM genesis_state_revision"
                    ).scalar_one()
                    == "0002_input"
                )
                if existing:
                    assert (
                        connection.exec_driver_sql("SELECT name FROM existing_records").scalar_one()
                        == "preserved"
                    )
                    assert (
                        connection.exec_driver_sql(
                            "SELECT version_num FROM alembic_version"
                        ).scalar_one()
                        == "unrelated"
                    )
        finally:
            engine.dispose()


def test_run_and_derived_version_preserve_original_and_utc_provenance(workflow):
    request = mutation("create")
    with pytest.raises(InvalidCommand):
        workflow.create_run(SCOPE, request)
    workflow.register_version(
        SCOPE.project_id, SCOPE.version_id, SCOPE.version_id, BASELINE, mutation("original")
    )
    workflow.register_version(
        SCOPE.project_id, "version:derived", SCOPE.version_id, "d" * 64, mutation("derived")
    )
    for wrong in (
        SCOPE.model_copy(update={"version_id": "version:derived"}),
        SCOPE.model_copy(update={"project_id": "project:different"}),
        SCOPE.model_copy(update={"baseline_sha256": "e" * 64}),
    ):
        with pytest.raises(InvalidCommand):
            workflow.create_run(wrong, request)
    workflow.create_run(SCOPE, request)
    assert repr(request) == "Mutation(actor_id='actor:fixture')"
    with pytest.raises(RecordConflict):
        workflow.register_version(
            SCOPE.project_id, SCOPE.version_id, SCOPE.version_id, "f" * 64, mutation("overwrite")
        )
    version = next(row for row in rows(workflow, versions) if row.id == SCOPE.version_id)
    (run,) = rows(workflow, runs)
    (event,) = rows(workflow, events)
    assert version.manifest_sha256 == BASELINE
    assert run.v0_id == version.id and run.actor_id == event.actor_id == "actor:fixture"
    assert run.created_at == event.created_at == utc_timestamp(run.created_at)
    assert all(len(row.key_sha256) == 64 for row in rows(workflow, mutations))


def test_workflow_requires_both_approvals_and_preserves_attempts(workflow):
    add_run(workflow)
    state = State.UPLOADED
    for next_state in (
        State.BASELINE_CREATED,
        State.LANGUAGE_ROUTED,
        State.ANALYZING,
        State.FINDINGS_READY,
        State.AWAITING_ISSUE_SELECTION,
    ):
        workflow.transition(SCOPE.run_id, state, next_state, mutation(next_state))
        state = next_state
    with pytest.raises(InvalidTransition):
        workflow.enqueue_transition(SCOPE.run_id, state, State.REFACTORING, mutation("bypass"))
    with pytest.raises(InvalidTransition):
        workflow.record_approval(
            SCOPE.run_id, Gate.PATCH_APPROVAL, "approval:early", "e" * 64, mutation("unsupported")
        )
    workflow.record_approval(
        SCOPE.run_id, Gate.ISSUE_SELECTION, "approval:issues", "c" * 64, mutation("first")
    )
    with pytest.raises(DuplicateMutation):
        workflow.record_approval(
            SCOPE.run_id, Gate.ISSUE_SELECTION, "approval:other", "d" * 64, mutation("first")
        )
    workflow.record_attempt(SCOPE.run_id, "attempt:one", mutation("attempt"))
    workflow.transition(
        SCOPE.run_id, State.REFACTORING, State.VALIDATING_CANDIDATES, mutation("validate")
    )
    workflow.transition(
        SCOPE.run_id, State.VALIDATING_CANDIDATES, State.AWAITING_PATCH_APPROVAL, mutation("await")
    )
    with pytest.raises(InvalidTransition):
        workflow.transition(
            SCOPE.run_id,
            State.AWAITING_PATCH_APPROVAL,
            State.COMBINED_VALIDATION,
            mutation("bypass"),
        )
    workflow.record_approval(
        SCOPE.run_id, Gate.PATCH_APPROVAL, "approval:patches", "d" * 64, mutation("second")
    )
    workflow.transition(SCOPE.run_id, State.COMBINED_VALIDATION, State.FINALIZED, mutation("final"))
    workflow.transition(SCOPE.run_id, State.FINALIZED, State.REPORT_READY, mutation("report"))
    assert [row.id for row in rows(workflow, attempts)] == ["attempt:one"]
    assert [row.id for row in rows(workflow, approvals)] == ["approval:issues", "approval:patches"]
    assert rows(workflow, runs)[0].state == State.REPORT_READY
    with pytest.raises(InvalidTransition):
        workflow.transition(
            SCOPE.run_id, State.REPORT_READY, State.USER_CANCELLED, mutation("terminal")
        )


async def test_post_duplicate_and_illegal_transition_have_one_durable_effect(workflow):
    add_run(workflow)
    app = FastAPI()

    @app.post("/test-transitions")
    def transition(request: Request, target: State):
        try:
            workflow.transition(
                SCOPE.run_id, State.UPLOADED, target, post_mutation(request, "actor:fixture")
            )
        except WorkflowError as error:
            return workflow_error_response(error, "request:fixture")
        return {"state": target}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"Idempotency-Key": "opaque-replay-token"}
        illegal = await client.post("/test-transitions?target=FINALIZED", headers=headers)
        assert illegal.status_code == 409
        accepted = await client.post("/test-transitions?target=BASELINE_CREATED", headers=headers)
        assert accepted.is_success
        duplicate = await client.post("/test-transitions?target=BASELINE_CREATED", headers=headers)
        assert duplicate.status_code == 409
        assert ErrorEnvelope.model_validate(duplicate.json()).code == "VALIDATION_FAILED"
        assert "opaque-replay-token" not in duplicate.text
        missing = await client.post("/test-transitions?target=BASELINE_CREATED")
        assert missing.status_code == 422
    assert [row.target_state for row in rows(workflow, events)] == [
        State.UPLOADED,
        State.BASELINE_CREATED,
    ]


def test_lost_delivery_retry_and_concurrent_workers_have_one_effect(workflow, tmp_path):
    add_run(workflow)
    job_id = workflow.enqueue_transition(
        SCOPE.run_id, State.UPLOADED, State.BASELINE_CREATED, mutation("enqueue")
    )
    with pytest.raises(RecordConflict):
        workflow.enqueue_transition(
            SCOPE.run_id, State.UPLOADED, State.BASELINE_CREATED, mutation("second-enqueue")
        )
    queue = Mock()
    queue.enqueue_call.side_effect = RedisConnectionError("broker unavailable")
    now = datetime.now(UTC)
    with pytest.raises(RedisConnectionError):
        dispatch_pending(workflow.engine, queue, now=now)
    assert rows(workflow, jobs)[0].status == "QUEUED"
    queue.enqueue_call.side_effect = None
    assert dispatch_pending(workflow.engine, queue, now=now) == 0
    restarted = Workflow(state_engine(tmp_path / "state.db"))
    try:
        retry = now + timedelta(seconds=REDELIVERY_SECONDS)
        assert dispatch_pending(restarted.engine, queue, now=retry) == 1
        assert queue.enqueue_call.call_args.kwargs["args"] == (job_id,)
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(restarted.complete_job, [job_id, job_id])) == [False, True]
        assert dispatch_pending(restarted.engine, queue, now=retry) == 0
    finally:
        restarted.engine.dispose()
    assert rows(workflow, jobs)[0].status == "COMPLETED"
    assert sum(row.job_id == job_id for row in rows(workflow, events)) == 1


def test_cancelled_run_supersedes_pending_jobs(workflow):
    add_run(workflow)
    job_id = workflow.enqueue_transition(
        SCOPE.run_id, State.UPLOADED, State.BASELINE_CREATED, mutation("enqueue")
    )
    workflow.transition(SCOPE.run_id, State.UPLOADED, State.USER_CANCELLED, mutation("cancel"))
    assert not workflow.complete_job(job_id)
    assert dispatch_pending(workflow.engine, Mock()) == 0
    assert rows(workflow, jobs)[0].status == "SUPERSEDED"
    assert rows(workflow, runs)[0].state == State.USER_CANCELLED
