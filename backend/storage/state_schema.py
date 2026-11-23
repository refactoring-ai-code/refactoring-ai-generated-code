"""Initial F02-STATE schema shared by the repository and migration 0001."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)

metadata = MetaData()

versions = Table(
    "genesis_versions",
    metadata,
    Column("id", String, primary_key=True),
    Column("project_id", String, nullable=False),
    Column("v0_id", ForeignKey("genesis_versions.id"), nullable=False),
    Column("manifest_sha256", String(64), nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
)
runs = Table(
    "genesis_runs",
    metadata,
    Column("id", String, primary_key=True),
    Column("analysis_id", String, nullable=False, unique=True),
    Column("v0_id", ForeignKey("genesis_versions.id"), nullable=False),
    Column("source_revision", String(40), nullable=False),
    Column("state", String, nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
)
approvals = Table(
    "genesis_approvals",
    metadata,
    Column("id", String, primary_key=True),
    Column("run_id", ForeignKey("genesis_runs.id"), nullable=False),
    Column("gate", String, nullable=False),
    Column("fingerprint", String(64), nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
    UniqueConstraint("run_id", "gate"),
)
attempts = Table(
    "genesis_attempts",
    metadata,
    Column("id", String, primary_key=True),
    Column("run_id", ForeignKey("genesis_runs.id"), nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
)
mutations = Table(
    "genesis_mutations",
    metadata,
    Column("actor_id", String, primary_key=True),
    Column("operation", String, primary_key=True),
    Column("target_id", String, primary_key=True),
    Column("key_sha256", String(64), primary_key=True),
    Column("created_at", String(27), nullable=False),
)
jobs = Table(
    "genesis_jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("run_id", ForeignKey("genesis_runs.id"), nullable=False),
    Column("source_state", String, nullable=False),
    Column("target_state", String, nullable=False),
    Column("status", String, nullable=False),
    Column("dispatch_after", String(27), nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
    Column("finished_at", String(27)),
    UniqueConstraint("run_id", "source_state"),
    CheckConstraint("status IN ('QUEUED', 'COMPLETED', 'SUPERSEDED')"),
    Index("ix_genesis_jobs_dispatch", "status", "dispatch_after", "id"),
)
events = Table(
    "genesis_state_events",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("run_id", ForeignKey("genesis_runs.id"), nullable=False, index=True),
    Column("source_state", String),
    Column("target_state", String, nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
    Column("job_id", ForeignKey("genesis_jobs.id"), unique=True),
)
