"""Bounded health probes for the development Redis and SQLite services."""

from __future__ import annotations

import asyncio
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff
from redis.exceptions import RedisError

PROBE_TIMEOUT_SECONDS = 1.0
CLEANUP_TIMEOUT_SECONDS = 0.2


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    name: str
    status: str
    reason: str | None = None

    @property
    def ready(self) -> bool:
        return self.status == "ready"

    def as_response(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


def check_storage(database_path: Path) -> ComponentHealth:
    """Check that the configured SQLite location is writable and queryable."""

    try:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database_path, timeout=PROBE_TIMEOUT_SECONDS)) as connection:
            # Exercise the persistent database, not a constant expression or TEMP table.
            # The identifier is generated locally and cannot contain SQL syntax.
            table = f"__genesis_health_{uuid4().hex}"
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(f'CREATE TABLE "{table}" (value INTEGER)')
                connection.execute(f'INSERT INTO "{table}" VALUES (?)', (1,))
                result = connection.execute(f'SELECT value FROM "{table}"').fetchone()
                if result != (1,):
                    return ComponentHealth("storage", "unavailable", "unexpected_probe_result")
            finally:
                # Health checks must not leave application data or schema changes behind.
                connection.rollback()
    except (OSError, sqlite3.Error):
        return ComponentHealth("storage", "unavailable", "connection_failed")
    return ComponentHealth("storage", "ready")


async def check_redis(redis_url: str) -> ComponentHealth:
    """Ping Redis without returning connection details or credentials."""

    client: Redis | None = None
    try:
        client = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=PROBE_TIMEOUT_SECONDS,
            socket_timeout=PROBE_TIMEOUT_SECONDS,
            retry=Retry(NoBackoff(), 0),
        )
        async with asyncio.timeout(PROBE_TIMEOUT_SECONDS):
            if not await client.ping():
                return ComponentHealth("redis", "unavailable", "unexpected_probe_result")
    except (OSError, RedisError, ValueError):
        return ComponentHealth("redis", "unavailable", "connection_failed")
    finally:
        if client is not None:
            try:
                async with asyncio.timeout(CLEANUP_TIMEOUT_SECONDS):
                    await client.aclose()
            except (OSError, RedisError):
                pass
    return ComponentHealth("redis", "ready")
