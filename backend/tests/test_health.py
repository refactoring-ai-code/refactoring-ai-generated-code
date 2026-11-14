from __future__ import annotations

import asyncio
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from backend.app import health, main
from backend.app.health import ComponentHealth
from httpx import ASGITransport, AsyncClient
from redis.exceptions import RedisError


def api_client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test")


@pytest.mark.asyncio
async def test_liveness_reports_ok() -> None:
    async with api_client() as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_reports_all_components(monkeypatch: pytest.MonkeyPatch) -> None:
    async def ready_redis(_: str) -> ComponentHealth:
        return ComponentHealth("redis", "ready")

    monkeypatch.setattr(main, "check_storage", lambda _: ComponentHealth("storage", "ready"))
    monkeypatch.setattr(main, "check_redis", ready_redis)

    async with api_client() as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "components": {
            "storage": {"name": "storage", "status": "ready"},
            "redis": {"name": "redis", "status": "ready"},
        },
    }


@pytest.mark.asyncio
async def test_readiness_fails_closed_without_redis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unavailable_redis(_: str) -> ComponentHealth:
        return ComponentHealth("redis", "unavailable", "connection_failed")

    monkeypatch.setattr(main, "check_storage", lambda _: ComponentHealth("storage", "ready"))
    monkeypatch.setattr(main, "check_redis", unavailable_redis)

    async with api_client() as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["components"]["redis"] == {
        "name": "redis",
        "status": "unavailable",
        "reason": "connection_failed",
    }


def test_storage_probe_uses_real_sqlite(tmp_path: Path) -> None:
    result = health.check_storage(tmp_path / "health.db")

    assert result == ComponentHealth("storage", "ready")


def test_storage_probe_rejects_corrupt_database(tmp_path: Path) -> None:
    database = tmp_path / "corrupt.db"
    database.write_bytes(b"not a SQLite database" * 100)

    assert health.check_storage(database).status == "unavailable"


def test_storage_probe_rejects_read_only_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "readonly.db"
    with closing(sqlite3.connect(database)) as connection:
        connection.execute("CREATE TABLE existing (value INTEGER)")
        connection.commit()
    connect = sqlite3.connect
    monkeypatch.setattr(
        health.sqlite3,
        "connect",
        lambda *args, **kwargs: connect(f"{database.as_uri()}?mode=ro", uri=True),
    )

    assert health.check_storage(database).status == "unavailable"


def test_storage_probe_preserves_data_and_closes_connection(tmp_path: Path) -> None:
    database = tmp_path / "existing.db"
    with closing(sqlite3.connect(database)) as connection:
        connection.execute("CREATE TABLE existing (value INTEGER)")
        connection.execute("INSERT INTO existing VALUES (42)")
        connection.commit()

    assert health.check_storage(database).ready

    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT * FROM existing").fetchall() == [(42,)]
        assert connection.execute("SELECT name FROM sqlite_schema").fetchall() == [("existing",)]
    # Windows refuses this rename if the probe still owns an open file handle.
    database.rename(tmp_path / "moved.db")


@pytest.mark.asyncio
async def test_readiness_fails_closed_for_corrupt_storage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "private-storage.db"
    database.write_bytes(b"invalid SQLite contents" * 100)
    monkeypatch.setenv("GENESIS_DATABASE_PATH", str(database))

    async def ready_redis(_: str) -> ComponentHealth:
        return ComponentHealth("redis", "ready")

    monkeypatch.setattr(main, "check_redis", ready_redis)
    async with api_client() as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["components"]["storage"]["status"] == "unavailable"
    assert str(database) not in response.text


@pytest.mark.asyncio
async def test_redis_probe_bounds_slow_ping_and_still_closes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closed = asyncio.Event()

    class SlowRedis:
        @classmethod
        def from_url(cls, *_: object, **__: object) -> SlowRedis:
            return cls()

        async def ping(self) -> bool:
            await asyncio.Event().wait()
            return True

        async def aclose(self) -> None:
            closed.set()

    monkeypatch.setattr(health, "Redis", SlowRedis)
    monkeypatch.setattr(health, "PROBE_TIMEOUT_SECONDS", 0.01, raising=False)

    result = await asyncio.wait_for(health.check_redis("redis://example.invalid"), timeout=0.5)

    assert result.status == "unavailable"
    assert closed.is_set()


@pytest.mark.asyncio
async def test_redis_probe_bounds_slow_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    class SlowCloseRedis:
        @classmethod
        def from_url(cls, *_: object, **__: object) -> SlowCloseRedis:
            return cls()

        async def ping(self) -> bool:
            raise RedisError("private connection details")

        async def aclose(self) -> None:
            await asyncio.Event().wait()

    monkeypatch.setattr(health, "Redis", SlowCloseRedis)
    monkeypatch.setattr(health, "CLEANUP_TIMEOUT_SECONDS", 0.01, raising=False)

    result = await asyncio.wait_for(health.check_redis("redis://example.invalid"), timeout=0.5)

    assert result == ComponentHealth("redis", "unavailable", "connection_failed")


@pytest.mark.asyncio
async def test_redis_probe_closes_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRedis:
        closed = False

        @classmethod
        def from_url(cls, *_: object, **__: object) -> FakeRedis:
            return cls()

        async def ping(self) -> bool:
            return True

        async def aclose(self) -> None:
            type(self).closed = True

    monkeypatch.setattr(health, "Redis", FakeRedis)

    result = await health.check_redis("redis://example.invalid/0")

    assert result == ComponentHealth("redis", "ready")
    assert FakeRedis.closed is True


@pytest.mark.asyncio
async def test_redis_probe_redacts_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingRedis:
        @classmethod
        def from_url(cls, *_: object, **__: object) -> FailingRedis:
            return cls()

        async def ping(self) -> bool:
            raise RedisError("redis://user:secret@example.invalid")

        async def aclose(self) -> None:
            return None

    monkeypatch.setattr(health, "Redis", FailingRedis)

    result = await health.check_redis("redis://user:secret@example.invalid/0")

    assert result == ComponentHealth("redis", "unavailable", "connection_failed")
    assert "secret" not in str(result)


@pytest.mark.asyncio
async def test_redis_probe_fails_closed_for_invalid_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class InvalidRedis:
        @classmethod
        def from_url(cls, *_: object, **__: object) -> InvalidRedis:
            raise ValueError("redis://user:secret@example.invalid")

    monkeypatch.setattr(health, "Redis", InvalidRedis)

    result = await health.check_redis("redis://user:secret@example.invalid/0")

    assert result == ComponentHealth("redis", "unavailable", "connection_failed")
    assert "secret" not in str(result)
