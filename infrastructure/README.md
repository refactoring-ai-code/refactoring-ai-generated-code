# Development services

F01-ENV provides a reproducible trusted development shell. It does not execute
uploaded or otherwise untrusted source code. Sandbox execution remains the
separate F06-SANDBOX task.

Pinned toolchains:

- Python 3.13.17 with `uv` 0.13.7
- Node.js 24.22.2 LTS with its bundled npm 11.19.1
- Redis 8.4.8 Alpine image pinned by digest

## Local package checks

Install the pinned Python and Node.js versions above first. Verify that
`node --version` prints `v24.22.2` and `npm --version` prints `11.19.1`.
Run the following from the repository root on Windows PowerShell:

```powershell
py -3.13 -m pip install uv==0.13.7
py -3.13 -m uv sync --project backend --locked
py -3.13 -m uv run --project backend python -m ruff check backend/app backend/tests
py -3.13 -m uv run --project backend python -m pytest backend/tests
Push-Location frontend
try {
    npm.cmd ci --ignore-scripts
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed" }
    npm.cmd run check
    if ($LASTEXITCODE -ne 0) { throw "Frontend checks failed" }
} finally {
    Pop-Location
}
```

On macOS, including Apple Silicon, run from the repository root:

```sh
python3.13 -m pip install uv==0.13.7
python3.13 -m uv sync --project backend --locked
python3.13 -m uv run --project backend python -m ruff check backend/app backend/tests
python3.13 -m uv run --project backend python -m pytest backend/tests
(cd frontend && npm ci --ignore-scripts && npm run check)
```

`backend/.python-version` and `frontend/.nvmrc` record the intended exact
versions. The backend lock is cross-platform; `uv` selects Python 3.13.17 for
the project environment. The npm lock is consumed with `npm ci --ignore-scripts`.

## Compose stack

Docker Desktop or another Docker Engine with Compose v2 is required. From the
repository root:

```powershell
.\infrastructure\dev.ps1 up
```

```sh
sh infrastructure/dev.sh up
```

The stack binds only the frontend (`127.0.0.1:5173`) and backend
(`127.0.0.1:8000`) to the local machine. Redis is not published. The API
provides `/health/live` and `/health/ready`; readiness checks both Redis and the
SQLite storage volume. Containers run without a Docker socket, without host
source mounts and with `no-new-privileges`.

Readiness returns HTTP 503 when either dependency is unavailable, without
exposing connection credentials or filesystem paths. SQLite is checked with a
write/read transaction that is rolled back, and its connection is closed after
each probe. Redis has a one-second deadline, no automatic retries, and a separate
0.2-second cleanup deadline. The probes run concurrently; these are I/O bounds,
not a real-time guarantee under host resource exhaustion.

The Dockerfiles copy only the application inputs they need. Local `.env`
files, keys, uploads, dependency folders, and build outputs are excluded from
the image build contexts. The three pinned base images support both Linux
AMD64 and ARM64; macOS/Windows hosts require Docker's Linux container mode.

Windows package tests have been exercised locally. Native macOS installation
and Docker startup are still pending verification; the application-stack CI
workflow is prepared to check actual container health when the changes are
published.

Stop the stack with `down`. Use `config` to validate Compose configuration and
`logs` for the current container output.
