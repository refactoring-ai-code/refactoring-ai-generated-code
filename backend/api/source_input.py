"""Authenticated HTTP surface for Project Genesis source intake."""

from __future__ import annotations

import json
import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest
from typing import Annotated, Literal

from backend.app.config import Settings
from backend.core.workflow import Mutation, WorkflowError
from backend.core.workflow_http import post_mutation, workflow_error_response
from backend.storage.database import migrate_state, state_engine
from backend.storage.input_validation import (
    MAX_BODY_BYTES,
    MAX_ENTRIES,
    InputRejected,
    Intake,
    decode_bytes,
    zip_intake,
)
from backend.storage.source_snapshots import (
    CONSENT_KINDS,
    Policy,
    SnapshotCorrupt,
    SnapshotUnavailable,
    SourceSnapshots,
)
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/api", tags=["source intake"])
_TOKEN = re.compile(r"[0-9a-f]{64}")
_LABEL = re.compile(r"[A-Za-z0-9_.-]{1,64}")
_NO_CACHE = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}


class StrictBody(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Decision(StrictBody):
    version: str
    granted: bool


class ConsentDecisions(StrictBody):
    terms: Decision
    retention: Decision
    cloud_transmission: Decision
    dynamic_execution: Decision


class UploadBase(StrictBody):
    consents: ConsentDecisions
    selected_language: (
        Literal["java", "python", "javascript", "typescript", "csharp", "go", "cpp"] | None
    ) = None


class UploadZip(UploadBase):
    kind: Literal["zip"]
    data_base64: str


class FolderFile(StrictBody):
    path: str
    data_base64: str


class UploadFolder(UploadBase):
    kind: Literal["folder"]
    files: list[FolderFile] = Field(min_length=1, max_length=MAX_ENTRIES)


class UploadSnippet(UploadBase):
    kind: Literal["snippet"]
    filename: str
    text: str


_UPLOAD = TypeAdapter(
    Annotated[UploadZip | UploadFolder | UploadSnippet, Field(discriminator="kind")]
)


@dataclass(frozen=True)
class InputService:
    snapshots: SourceSnapshots
    policy: Policy
    actor_digests: dict[str, str]


def _reject_duplicate_keys(pairs: list[tuple]) -> dict:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("Duplicate JSON field.")
    return value


def _configured_input() -> tuple[Policy, dict[str, str]] | None:
    actors = os.getenv("GENESIS_INPUT_ACTOR_DIGESTS")
    raw_policy = os.getenv("GENESIS_INPUT_POLICY")
    if actors is None or raw_policy is None:
        return None
    try:
        digests = json.loads(actors, object_pairs_hook=_reject_duplicate_keys)
        payload = json.loads(raw_policy, object_pairs_hook=_reject_duplicate_keys)
        versions = payload["versions"]
        days = payload["retention_days"]
        if (
            not isinstance(digests, dict)
            or not 1 <= len(digests) <= 1000
            or len(set(digests.values())) != len(digests)
            or not isinstance(versions, dict)
            or set(versions) != set(CONSENT_KINDS)
            or any(not _LABEL.fullmatch(version) for version in versions.values())
            or type(days) is not int
            or not 1 <= days <= 3650
        ):
            return None
        for actor, digest in digests.items():
            Mutation(actor, "startup-validation")
            if not _TOKEN.fullmatch(digest):
                return None
    except (KeyError, TypeError, ValueError, RecursionError):
        return None
    return Policy(versions, days), digests


@asynccontextmanager
async def input_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Enable source intake only when authentication and policy are configured."""
    app.state.input_service = None
    config = _configured_input()
    if config is None:
        yield
        return
    policy, digests = config
    path = Settings.from_environment().database_path
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        # Health may already have created the file. Limit access before source writes.
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            path.chmod(0o600)
        else:
            os.close(descriptor)
    engine = state_engine(path)
    try:
        await run_in_threadpool(migrate_state, engine)
        app.state.input_service = InputService(SourceSnapshots(engine), policy, digests)
        yield
    finally:
        app.state.input_service = None
        engine.dispose()


def _identity(request: Request) -> tuple[InputService, str]:
    service = getattr(request.app.state, "input_service", None)
    if service is None:
        raise HTTPException(503, "Source intake is unavailable.", headers=_NO_CACHE)
    values = request.headers.getlist("Authorization")
    if len(values) == 1:
        scheme, _, token = values[0].partition(" ")
        if scheme.lower() == "bearer" and _TOKEN.fullmatch(token):
            supplied = sha256(token.encode("ascii")).hexdigest()
            for actor, digest in service.actor_digests.items():
                if compare_digest(supplied, digest):
                    return service, actor
    raise HTTPException(
        401,
        "Authentication required.",
        headers={**_NO_CACHE, "WWW-Authenticate": "Bearer"},
    )


def _snapshot_error(error: Exception) -> HTTPException:
    if isinstance(error, SnapshotUnavailable):
        return HTTPException(404, "Source snapshot is unavailable.", headers=_NO_CACHE)
    return HTTPException(503, "Source snapshot is unavailable.", headers=_NO_CACHE)


async def _request_body(request: Request) -> bytearray:
    if request.headers.get("content-type", "").split(";", 1)[0].lower() != "application/json":
        raise HTTPException(415, "A JSON request is required.", headers=_NO_CACHE)
    if request.headers.get("content-encoding", "identity").lower() != "identity":
        raise HTTPException(415, "Unsupported request encoding.", headers=_NO_CACHE)
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_BODY_BYTES:
            raise HTTPException(413, "Upload exceeds the request size limit.", headers=_NO_CACHE)
        body.extend(chunk)
    return body


def _upload(raw: bytearray, policy: Policy) -> tuple[UploadBase, Intake, dict[str, bool]]:
    try:
        request = _UPLOAD.validate_python(
            json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
        )
    except (ValueError, RecursionError):
        raise InputRejected("Invalid source intake request.") from None
    submissions = request.consents
    if any(getattr(submissions, key).version != policy.versions[key] for key in CONSENT_KINDS):
        raise InputRejected("Consent policy version no longer applies.")
    decisions = {key: getattr(submissions, key).granted for key in CONSENT_KINDS}
    if not decisions["terms"] or not decisions["retention"]:
        raise InputRejected("Explicit terms and retention consent are required.")
    if isinstance(request, UploadZip):
        return request, zip_intake(decode_bytes(request.data_base64)), decisions
    result = Intake()
    if isinstance(request, UploadFolder):
        for item in request.files:
            path = result.register(item.path)
            result.add_bytes(path, decode_bytes(item.data_base64))
    else:
        path = result.register(request.filename)
        try:
            data = request.text.encode("utf-8")
        except UnicodeError:
            raise InputRejected("Invalid snippet encoding.") from None
        result.add_bytes(path, data)
    return request, result.finish(), decisions


def _store_upload(raw: bytearray, service: InputService, mutation: Mutation) -> dict:
    upload, intake, decisions = _upload(raw, service.policy)
    return service.snapshots.create(
        intake, upload.kind, upload.selected_language, decisions, service.policy, mutation
    )


@router.get("/input-policy")
def input_policy(request: Request) -> JSONResponse:
    service, _ = _identity(request)
    return JSONResponse(
        {
            "versions": dict(service.policy.versions),
            "retention_days": service.policy.retention_days,
        },
        headers=_NO_CACHE,
    )


@router.post("/projects", status_code=201)
async def create_project(request: Request) -> JSONResponse:
    service, actor = _identity(request)
    try:
        mutation = post_mutation(request, actor)
        raw = await _request_body(request)
        result = await run_in_threadpool(_store_upload, raw, service, mutation)
    except WorkflowError as error:
        response = workflow_error_response(error, f"request:{os.urandom(16).hex()}")
        response.headers.update(_NO_CACHE)
        return response
    except InputRejected as error:
        raise HTTPException(422, str(error), headers=_NO_CACHE) from None
    except (SQLAlchemyError, SnapshotCorrupt, SnapshotUnavailable) as error:
        raise _snapshot_error(error) from None
    return JSONResponse(
        result,
        status_code=201,
        headers={**_NO_CACHE, "Location": f"/api/versions/{result['version_id']}/source"},
    )


@router.get("/versions/{version_id}/source")
def source_manifest(request: Request, version_id: str) -> JSONResponse:
    service, actor = _identity(request)
    try:
        return JSONResponse(service.snapshots.describe(actor, version_id), headers=_NO_CACHE)
    except (SQLAlchemyError, SnapshotCorrupt, SnapshotUnavailable) as error:
        raise _snapshot_error(error) from None


@router.get("/versions/{version_id}/source/download")
def source_download(request: Request, version_id: str) -> Response:
    service, actor = _identity(request)
    try:
        checksum, data = service.snapshots.download(actor, version_id)
    except (SQLAlchemyError, SnapshotCorrupt, SnapshotUnavailable) as error:
        raise _snapshot_error(error) from None
    return Response(
        data,
        media_type="application/zip",
        headers={
            **_NO_CACHE,
            "Content-Disposition": 'attachment; filename="source-v0.zip"',
            "X-Genesis-Manifest-Sha256": checksum,
        },
    )
