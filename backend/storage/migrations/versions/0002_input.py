"""Add immutable intake snapshot and consent storage."""

from alembic import op
from backend.storage.input_schema import metadata

revision = "0002_input"
down_revision = "0001_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in metadata.sorted_tables:
        table.create(op.get_bind(), checkfirst=False)
