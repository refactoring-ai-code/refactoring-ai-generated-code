"""Create workflow metadata without modifying other application tables."""

from alembic import op
from backend.storage.state_schema import metadata

revision = "0001_state"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in metadata.sorted_tables:
        table.create(op.get_bind(), checkfirst=False)
