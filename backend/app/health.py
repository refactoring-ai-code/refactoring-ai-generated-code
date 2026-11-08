"""Bounded health probes for the development Redis and SQLite services."""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError


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
        with sqlite3.connect(database_path, timeout=1.0) as connection:
            result = connection.execute("SELECT 1").fetchone()
        if result != (1,):
            return ComponentHealth("storage", "unavailable", "unexpected_probe_result")
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
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        if not await client.ping():
            return ComponentHealth("redis", "unavailable", "unexpected_probe_result")
    except (OSError, RedisError, ValueError):
        return ComponentHealth("redis", "unavailable", "connection_failed")
    finally:
        if client is not None:
            try:
                await client.aclose()
            except (OSError, RedisError):
                pass
    return ComponentHealth("redis", "ready")
