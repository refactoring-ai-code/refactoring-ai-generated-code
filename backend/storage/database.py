"""SQLite initialization and transactional writes for workflow metadata."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Connection, Engine, create_engine, event


def state_engine(database_path: Path) -> Engine:
    """Open the existing application database with enforceable foreign keys."""
    database_path = database_path.resolve()
    engine = create_engine(
        URL.create("sqlite+pysqlite", database=str(database_path)), hide_parameters=True
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys = ON").close()

    return engine


@contextmanager
def state_write(engine: Engine) -> Iterator[Connection]:
    # Serialize read/validate/write commands, including claims by different workers.
    with engine.begin() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        yield connection


def migrate_state(engine: Engine) -> None:
    """Apply transactional Alembic upgrades without adopting unrelated tables."""
    config = Config()
    directory = Path(__file__).with_name("migrations").as_posix()
    config.set_main_option("script_location", directory.replace("%", "%%"))
    with state_write(engine) as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
