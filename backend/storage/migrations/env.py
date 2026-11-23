"""Use the caller's SQLite connection and its existing write transaction."""

from alembic import context

context.configure(
    connection=context.config.attributes["connection"],
    version_table="genesis_state_revision",
)
with context.begin_transaction():
    context.run_migrations()
