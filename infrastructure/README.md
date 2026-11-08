# Development services

F01-ENV provides a reproducible trusted development shell. It does not execute
uploaded or otherwise untrusted source code. Sandbox execution remains the
separate F06-SANDBOX task.

Pinned toolchains:

- Python 3.13.17 with `uv` 0.13.7
- Node.js 24.22.2 LTS with its bundled npm 11.19.1
- Redis 8.4.8 Alpine image pinned by digest

## Local package checks

From the repository root:

```sh
python -m pip install uv==0.13.7
uv sync --project backend --locked
uv run --project backend ruff check backend/app backend/tests
uv run --project backend python -m pytest backend/tests
cd frontend
npm ci --ignore-scripts
npm run check
```

Use Python 3.13 on Windows (`py -3.13 -m pip ...`) or macOS (`python3.13 -m pip
...`). `backend/.python-version` and `frontend/.nvmrc` record the intended exact
versions. The backend lock is cross-platform; the npm lock is consumed with
`npm ci`.

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

Stop the stack with `down`. Use `config` to validate Compose configuration and
`logs` for the current container output.
