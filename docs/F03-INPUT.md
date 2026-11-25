# F03-INPUT source intake

[Issue #13](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/13)
implements bounded source intake, distinct policy decisions and owner-scoped V0
snapshots. The [F02 state layer](F02-STATE.md) consumes the registered version ID,
project ID and canonical manifest SHA-256.

## Enable and use the development API

With a trusted deployment configuration, set these variables before starting
`backend.app.main:app`. The application uses its existing locked backend
environment. Docker packages the same API and migrations.

- `GENESIS_INPUT_ACTOR_DIGESTS` is a JSON object mapping trusted `actor:<id>`
  identifiers to SHA-256 digests of independently generated random 32-byte
  bearer tokens. Encode the token itself as 64 lowercase hex characters and
  hash that ASCII text. Pass the original token only in an Authorization
  header and provision it securely outside source control. Use HTTPS if
  serving the API off loopback.
- `GENESIS_INPUT_POLICY` is a JSON object with `versions` containing
  `terms`, `retention`, `cloud_transmission` and `dynamic_execution` policy
  version identifiers, and a `retention_days` integer. Supply reviewed terms
  and retention decisions before enabling intake with real source. Show the
  applicable policy text to the source owner before collecting the decisions.
- `GENESIS_DATABASE_PATH` identifies the existing private SQLite database.
  The application upgrades it at startup when intake is configured. Use
  owner-controlled directories, volumes and backups. On Windows, the operator
  sets the application data directory ACL. Without valid intake configuration
  the routes return 503 and the existing health routes continue to work.

All four routes require the configured Authorization bearer header.

| Method and route | Result |
|---|---|
| `GET /api/input-policy` | Actual configured policy versions and retention period. |
| `POST /api/projects` | Create one project and its immutable V0. Send JSON and exactly one `Idempotency-Key`. |
| `GET /api/versions/{version_id}/source` | Owner-only manifest, expiry and four decision records. |
| `GET /api/versions/{version_id}/source/download` | Owner-only attachment containing verified V0 files. |

The POST body contains `kind`, optional `selected_language`, and `consents`.
Each consent field contains `version` and a JSON boolean `granted`. Terms and
retention must be granted. Cloud transmission and dynamic execution each
require a decision and can both be denied. The authenticated actor and UTC
time come from the server. A repeated accepted key for the same actor
returns 409. Rejected submissions can be corrected and retried with the
same key. A successful request returns the project ID, baseline version ID,
manifest and hashes, recorded decisions, and a relative Location.

- `zip` supplies one `data_base64` ZIP.
- `folder` supplies `files` containing `path` and `data_base64` for each
  regular file. The client supplies relative paths and regular-file bytes.
  The server never opens a local client path or URL.
- `snippet` supplies `filename` and `text` encoded as UTF-8.

## Intake and storage boundaries

The service allows 12 MiB of request JSON, 8 MiB of archive and total unpacked
bytes, 2 MiB per file and 256 entries. ZIP acceptance also caps compression
at 200:1 and central directory metadata at 256 KiB. Validation rejects
nonrelative paths, platform aliases, symlinks, special entries, ambiguous
case or Unicode aliases, unsupported compression and size violations. It
reads validated members into bounded memory and does not extract or execute
the uploaded archive. It never recursively unfolds embedded archives.
Names are normalized to NFC and accepted file bytes retain their exact line
endings. Detection uses extensions and reports unknown files explicitly. A
language hint is recorded independently of each detection.

The manifest reports excluded paths and reasons for tooling, build output,
potential credentials, platform metadata and unsupported binary/encoding
content. For ZIP inputs the exact submitted container and its SHA-256 are
preserved privately for provenance under the same retention policy. Neither
workers nor downloads consume that raw container. Upload only authorized
source, use secret-free archives and configure private storage. Owner
downloads are rebuilt from verified included files, with safe entry names,
an attachment disposition and no cache.

Version registration, manifest, file data, consents and the F02 request key
commit in one SQLite transaction. The canonical manifest and each included
file are verified before download and before and after work copy creation.
Trusted in-process workers obtain separate temporary candidate and final
copies via `SourceSnapshots.workspace`. Both start from V0, and the paths
are removed when the context closes. Actual sandbox execution, external
providers, final validation and user approvals beyond intake are separate
tasks.

Expired input is inaccessible. Operators can call
`SourceSnapshots.purge_expired()` from a trusted maintenance process with the
same configured database after migration. It removes expired manifests and
unreferenced source bytes, leaving audit metadata. Schedule this maintenance
and control database journals and backups in line with the approved
retention policy. This is logical deletion, not physical media erasure.

## Verification

Run `uv sync --project backend --locked` and then
`uv run --project backend --locked python -m pytest backend/tests`.
The intake tests cover authenticated API calls for all three input kinds,
unsafe archives, portable path collisions, denied and separate permissions,
single-write retries, owner-only download, expired artifacts, corruption
rejection and independent candidate/final copies. The tests bind the
created V0 to a real F02 run and verify that the original bytes survive
modifications to both copies.
