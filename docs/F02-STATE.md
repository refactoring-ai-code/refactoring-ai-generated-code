# F02-STATE workflow metadata and jobs

[Issue #12](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/12)
implements the workflow state and persistence required by FR-006, NFR-06 and
NFR-12. The initial migration adds namespaced SQLite tables for versions, runs,
the two approval gates, attempts, jobs, idempotency keys and state history.
Alembic tracks its revision in `genesis_state_revision` and preserves other
tables in the same database.

## Workflow boundary

[`Workflow`](../backend/core/workflow.py) takes typed IDs from the approved
CIR and links every new run to the registered original version for that project.
The supplied manifest hash must match the V0 registration. The service records
actor and UTC timestamp, preserves version and approval records, and records
each state change in the same transaction. The caller must establish the actor,
authorization and input evidence before invoking a command. File intake, byte
storage, Gate 1 eligibility and Gate 2 acceptance policy belong to their
respective integration tasks.

[`post_mutation`](../backend/core/workflow_http.py) reads one `Idempotency-Key`
header and binds it to the authenticated actor. The database stores a SHA-256
digest scoped by actor, operation and target. Reusing a committed key is a
conflict, including reuse with different submitted fields. A failed command
rolls back its key so a corrected submission can succeed. The POST adapter
returns HTTP 409 for conflicts and HTTP 422 for invalid input, using the existing
CIR error envelope. The backend tests mount the adapter on an isolated FastAPI
route. The deployed application remains the F01 health surface. The approved
OpenAPI IssueSelection route is integrated under F08-INTEGRATE.

## Run the migration and workers

Use the repository's locked backend environment. Both processes need the same
trusted `GENESIS_DATABASE_PATH` and `GENESIS_REDIS_URL` settings. The SQLite
file must be reachable from the dispatcher and worker. Use a dedicated Redis
service for the trusted internal queue.

```text
uv run --project backend --locked python -m backend.workers.state_queue migrate
uv run --project backend --locked python -m backend.workers.state_queue dispatch --watch
uv run --project backend --locked python -m backend.workers.state_queue worker
```

Run the migration first, then run the dispatcher and worker as separate
processes. A dispatcher without `--watch` sends one batch. A worker with
`--burst` drains available deliveries and exits. These entry points run from
the repository checkout. The development Compose stack continues to exercise
the health endpoints.

A queued transition and its request key commit to SQLite before Redis is
contacted. The dispatcher reserves each delivery for 30 seconds, after which
an unfinished job can be sent again. RQ carries only a job ID with JSON
serialization. Worker state changes, the audit record and job completion
commit together. A process loss before commit leaves the job pending. Replayed
or concurrent deliveries after a commit leave the result intact. Cancelling
the run supersedes its pending transitions. This guarantee covers workflow
metadata writes. External providers and sandbox execution are separate tasks.

## Verify

```text
uv sync --project backend --locked
uv run --project backend --locked ruff check backend/app backend/tests
uv run --project backend --locked python -m pytest backend/tests
```

To test actual worker restart, set `GENESIS_STATE_TEST_REDIS_URL` to a fresh,
dedicated Redis test database, then run the following command. The test exits
a worker after its SQLite writes and before commit, verifies rollback, and
uses a new worker process to consume repeated RQ deliveries.

```text
uv run --project backend --locked python -m pytest -c backend/pyproject.toml tests/state/test_redis_restart.py
```
