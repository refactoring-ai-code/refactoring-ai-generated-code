from __future__ import annotations

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
