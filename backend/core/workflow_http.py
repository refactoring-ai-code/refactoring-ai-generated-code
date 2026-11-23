"""Shared POST boundary for authorized workflow callers."""

from backend.core.schemas.models import ErrorEnvelope
from backend.core.workflow import InvalidCommand, Mutation, RecordConflict, WorkflowError
from fastapi import Request
from fastapi.responses import JSONResponse


def post_mutation(request: Request, authenticated_actor_id: str) -> Mutation:
    """Bind one request key to the actor established by the caller's auth layer."""
    keys = request.headers.getlist("Idempotency-Key")
    if len(keys) != 1:
        raise InvalidCommand("Exactly one idempotency key is required.")
    return Mutation(authenticated_actor_id, keys[0])


def workflow_error_response(error: WorkflowError, request_id: str) -> JSONResponse:
    conflict = isinstance(error, RecordConflict)
    body = ErrorEnvelope(
        schema_version="1.0.0",
        request_id=request_id,
        status="ERROR",
        component="API",
        code="VALIDATION_FAILED" if conflict else "INVALID_CONTRACT",
        message="The workflow mutation conflicts with recorded state."
        if conflict
        else "The workflow mutation is invalid.",
        retryable=False,
        details=[],
    )
    return JSONResponse(status_code=409 if conflict else 422, content=body.model_dump(mode="json"))
