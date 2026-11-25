"""Persist owner-scoped V0 bytes and materialize isolated working copies."""

from __future__ import annotations

import io
import json
import zipfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from uuid import uuid4

import rfc8785
from backend.core.workflow import Mutation, _record_mutation, utc_now
from backend.storage.database import state_write
from backend.storage.input_schema import blobs, consents, files, snapshots
from backend.storage.input_validation import Intake, relative_path
from backend.storage.state_schema import versions
from sqlalchemy import Connection, Engine, exists, select
from sqlalchemy.dialects.sqlite import insert

CONSENT_KINDS = ("terms", "retention", "cloud_transmission", "dynamic_execution")


class SnapshotUnavailable(LookupError):
    """The requested snapshot does not exist or the actor cannot access it."""


class SnapshotCorrupt(RuntimeError):
    """Stored content no longer matches its original manifest."""


@dataclass(frozen=True)
class Policy:
    versions: Mapping[str, str]
    retention_days: int


@dataclass(frozen=True)
class Derivative:
    baseline_version_id: str
    baseline_sha256: str
    kind: Literal["candidate", "final"]
    path: Path


def _expiry(now: str, days: int) -> str:
    time = datetime.fromisoformat(now) + timedelta(days=days)
    return time.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _put_blob(connection: Connection, digest: str, data: bytes) -> None:
    result = connection.execute(
        insert(blobs).values(sha256=digest, data=data).on_conflict_do_nothing()
    )
    if (
        result.rowcount != 1
        and connection.scalar(select(blobs.c.data).where(blobs.c.sha256 == digest)) != data
    ):
        raise SnapshotCorrupt("Stored content differs from its hash.")


class SourceSnapshots:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create(
        self,
        intake: Intake,
        kind: str,
        selected_language: str | None,
        decisions: Mapping[str, bool],
        policy: Policy,
        mutation: Mutation,
    ) -> dict:
        # The API verifies decisions against the current operator policy before parsing bytes.
        if set(decisions) != set(CONSENT_KINDS) or not (
            decisions["terms"] and decisions["retention"]
        ):
            raise ValueError("Explicit terms and retention consent are required.")
        project_id = f"project:{uuid4().hex}"
        version_id = f"version:{uuid4().hex}"
        records = []
        for item in sorted(intake.files, key=lambda f: f.path):
            records.append(
                {
                    "path": item.path,
                    "size": len(item.data),
                    "sha256": sha256(item.data).hexdigest(),
                    "detected_language": item.language,
                    "is_source": item.language != "unknown",
                    "access_mode": "owner",
                }
            )
        manifest = {
            "schema_version": "1.0",
            "files": records,
            "excluded": sorted(intake.excluded, key=lambda item: item["path"]),
        }
        manifest_bytes = rfc8785.dumps(manifest)
        manifest_hash = sha256(manifest_bytes).hexdigest()
        archive = intake.original_zip
        archive_hash = sha256(archive).hexdigest() if archive is not None else None
        now = utc_now()
        expires_at = _expiry(now, policy.retention_days)
        with state_write(self.engine) as connection:
            # Use the existing F02 key table and rejection behavior in this same transaction.
            _record_mutation(connection, mutation, "create_input", "intake", now)
            connection.execute(
                versions.insert().values(
                    id=version_id,
                    project_id=project_id,
                    v0_id=version_id,
                    manifest_sha256=manifest_hash,
                    actor_id=mutation.actor_id,
                    created_at=now,
                )
            )
            if archive is not None:
                _put_blob(connection, archive_hash, archive)
            connection.execute(
                snapshots.insert().values(
                    version_id=version_id,
                    manifest=manifest_bytes,
                    input_kind=kind,
                    selected_language=selected_language,
                    upload_sha256=archive_hash,
                    original_zip_sha256=archive_hash,
                    expires_at=expires_at,
                )
            )
            data = {file.path: file.data for file in intake.files}
            for record in records:
                _put_blob(connection, record["sha256"], data[record["path"]])
                connection.execute(
                    files.insert().values(
                        version_id=version_id,
                        path=record["path"],
                        sha256=record["sha256"],
                    )
                )
            connection.execute(
                consents.insert(),
                [
                    dict(
                        version_id=version_id,
                        kind=name,
                        policy_version=policy.versions[name],
                        granted=decisions[name],
                        actor_id=mutation.actor_id,
                        created_at=now,
                    )
                    for name in CONSENT_KINDS
                ],
            )
        return self.describe(mutation.actor_id, version_id)

    def _snapshot(self, db: Connection, actor_id: str, version_id: str) -> tuple:
        row = (
            db.execute(
                select(
                    snapshots,
                    versions.c.project_id,
                    versions.c.created_at,
                    versions.c.manifest_sha256,
                )
                .join(versions, versions.c.id == snapshots.c.version_id)
                .where(
                    versions.c.actor_id == actor_id,
                    snapshots.c.version_id == version_id,
                    snapshots.c.expires_at > utc_now(),
                    snapshots.c.purged_at.is_(None),
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise SnapshotUnavailable()
        if row["manifest"] is None or sha256(row["manifest"]).hexdigest() != row["manifest_sha256"]:
            raise SnapshotCorrupt("Stored manifest differs from its hash.")
        return row, json.loads(row["manifest"])

    def describe(self, actor_id: str, version_id: str) -> dict:
        with self.engine.begin() as db:
            db.exec_driver_sql("BEGIN")
            row, manifest = self._snapshot(db, actor_id, version_id)
            decisions = db.execute(
                select(
                    consents.c.kind,
                    consents.c.policy_version,
                    consents.c.granted,
                    consents.c.actor_id,
                    consents.c.created_at,
                )
                .where(consents.c.version_id == version_id)
                .order_by(consents.c.kind)
            ).mappings()
            return {
                **{
                    k: row[k]
                    for k in (
                        "version_id",
                        "project_id",
                        "created_at",
                        "manifest_sha256",
                        "input_kind",
                        "upload_sha256",
                        "selected_language",
                        "expires_at",
                    )
                },
                "manifest": manifest,
                "consents": [dict(item) for item in decisions],
            }

    def _verified_files(self, actor_id: str, version_id: str) -> tuple[str, dict[str, bytes]]:
        with self.engine.begin() as db:
            db.exec_driver_sql("BEGIN")
            row, manifest = self._snapshot(db, actor_id, version_id)
            if row["original_zip_sha256"]:
                archive = db.scalar(
                    select(blobs.c.data).where(
                        blobs.c.sha256 == row["original_zip_sha256"],
                    )
                )
                if archive is None or sha256(archive).hexdigest() != row["upload_sha256"]:
                    raise SnapshotCorrupt("Stored original archive differs from its hash.")
            stored = {
                path: (digest, data)
                for path, digest, data in db.execute(
                    select(files.c.path, files.c.sha256, blobs.c.data)
                    .join(blobs, blobs.c.sha256 == files.c.sha256)
                    .where(files.c.version_id == version_id)
                )
            }
            expected = {item["path"]: item for item in manifest["files"]}
            if set(stored) != set(expected):
                raise SnapshotCorrupt("Stored paths differ from the manifest.")
            for path, (digest, data) in stored.items():
                item = expected[path]
                if (
                    relative_path(path) != path
                    or len(data) != item["size"]
                    or sha256(data).hexdigest() != digest
                    or digest != item["sha256"]
                ):
                    raise SnapshotCorrupt("Stored file differs from the manifest.")
            return row["manifest_sha256"], {path: item[1] for path, item in stored.items()}

    def download(self, actor_id: str, version_id: str) -> tuple[str, bytes]:
        manifest_hash, payload = self._verified_files(actor_id, version_id)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as archive:
            for path, data in sorted(payload.items()):
                info = zipfile.ZipInfo(path)
                info.create_system = 3
                info.external_attr = 0o100600 << 16
                archive.writestr(info, data)
        return manifest_hash, out.getvalue()

    @contextmanager
    def workspace(
        self, actor_id: str, version_id: str, kind: Literal["candidate", "final"]
    ) -> Iterator[Derivative]:
        """For trusted workers. Each invocation starts from verified V0."""
        if kind not in ("candidate", "final"):
            raise ValueError("Unknown derivative kind.")
        checksum, payload = self._verified_files(actor_id, version_id)
        with TemporaryDirectory(prefix=f"genesis-{kind}-") as name:
            root = Path(name)
            for path, data in payload.items():
                target = root.joinpath(*path.split("/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(data)
            try:
                yield Derivative(version_id, checksum, kind, root)
            finally:
                after, _ = self._verified_files(actor_id, version_id)
                if after != checksum:
                    raise SnapshotCorrupt("V0 changed during derivative work.")

    def purge_expired(self) -> int:
        """Operator cleanup. Keep audit metadata and remove only expired payloads."""
        now = utc_now()
        with state_write(self.engine) as db:
            expired = select(snapshots.c.version_id).where(
                snapshots.c.expires_at <= now,
                snapshots.c.purged_at.is_(None),
            )
            db.execute(files.delete().where(files.c.version_id.in_(expired)))
            result = db.execute(
                snapshots.update()
                .where(snapshots.c.version_id.in_(expired))
                .values(manifest=None, original_zip_sha256=None, purged_at=now)
            )
            db.execute(
                blobs.delete().where(
                    ~exists(select(files.c.sha256).where(files.c.sha256 == blobs.c.sha256)),
                    ~exists(
                        select(snapshots.c.original_zip_sha256).where(
                            snapshots.c.original_zip_sha256 == blobs.c.sha256,
                        )
                    ),
                )
            )
            return result.rowcount
