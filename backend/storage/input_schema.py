"""Intake tables added independently of the F02-STATE migration."""

from backend.storage.state_schema import versions
from sqlalchemy import Boolean, Column, ForeignKey, LargeBinary, MetaData, String, Table

metadata = MetaData()

blobs = Table(
    "genesis_input_blobs",
    metadata,
    Column("sha256", String(64), primary_key=True),
    Column("data", LargeBinary, nullable=False),
)
snapshots = Table(
    "genesis_input_snapshots",
    metadata,
    Column("version_id", ForeignKey(versions.c.id), primary_key=True),
    Column("manifest", LargeBinary),
    Column("input_kind", String, nullable=False),
    Column("selected_language", String),
    Column("upload_sha256", String(64)),
    Column("original_zip_sha256", ForeignKey(blobs.c.sha256)),
    Column("expires_at", String(27), nullable=False, index=True),
    Column("purged_at", String(27)),
)
files = Table(
    "genesis_input_files",
    metadata,
    Column("version_id", ForeignKey(snapshots.c.version_id), primary_key=True),
    Column("path", String, primary_key=True),
    Column("sha256", ForeignKey(blobs.c.sha256), nullable=False),
)
consents = Table(
    "genesis_input_consents",
    metadata,
    Column("version_id", ForeignKey(snapshots.c.version_id), primary_key=True),
    Column("kind", String, primary_key=True),
    Column("policy_version", String, nullable=False),
    Column("granted", Boolean, nullable=False),
    Column("actor_id", String, nullable=False),
    Column("created_at", String(27), nullable=False),
)
