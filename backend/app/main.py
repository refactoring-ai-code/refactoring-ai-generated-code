"""Project Genesis development API."""

from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from backend.api.source_input import input_lifespan
from backend.api.source_input import router as input_router
from backend.app.config import Settings
from backend.app.health import ComponentHealth, check_redis, check_storage

app = FastAPI(title="Project Genesis", version="0.1.0", lifespan=input_lifespan)
app.include_router(input_router)


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Report that the API process can serve requests."""

    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> JSONResponse:
    """Report bounded readiness for the required development services."""

    settings = Settings.from_environment()
    storage, redis = await asyncio.gather(
        run_in_threadpool(check_storage, settings.database_path),
        check_redis(settings.redis_url),
    )
    components: tuple[ComponentHealth, ...] = (storage, redis)
    ready = all(component.ready for component in components)
    return JSONResponse(
        status_code=200 if ready else 503,
        content={
            "status": "ready" if ready else "unavailable",
            "components": {component.name: component.as_response() for component in components},
        },
    )
