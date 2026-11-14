# First approval fixture workspace — F08-UI / #21

This frontend implements the Issue Explorer and local choice preview for the first
approval screen. **Every scenario is a fixture.** It does not call an analysis
API, save an authenticated approval, start refactoring, or implement F08-INTEGRATE.

## Run and verify

Use the pinned **Node.js 24.22.2 and npm 11.19.1** toolchain. From `frontend/`:

```text
npm ci --ignore-scripts
npm run test
npm run build
npm run check
npm run dev -- --host 127.0.0.1
```

`check` runs the contract-copy/type check, Vitest and the production TypeScript/Vite
build. The tests include real React DOM interactions; only the Monaco rendering
module is replaced in those tests. Actual Monaco loading, read-only behavior,
duplicate location navigation, error recovery and desktop/mobile layouts were
also checked manually in the production preview. DOM unit tests alone do not
establish browser-worker or platform compatibility.

## Fixture and contract boundary

The authoritative [OpenAPI](../docs/contracts/openapi-1.0.0.json),
[CIR schema](../backend/core/schemas/cir-1.0.0.schema.json),
[result](../docs/contracts/examples/result.json),
[selection reference](../docs/contracts/examples/issue-selection.json), and
[safe error](../docs/contracts/examples/error.json) are unchanged.

`scripts/contracts.mjs` checks that OpenAPI and CIR share the complete definition
registry, generates consumer TypeScript types and copies the schema/examples
byte-for-byte into `src/contracts/`. These are generated consumer artifacts, not
independent contract definitions. `npm run contracts:check`, also required by
`npm run test`, rejects any drift against canonical source files. Regenerate
after an independently authorized contract update with `npm run contracts:sync`;
do not hand-edit the generated files. The existing frontend-only Docker build
uses these checked-in artifacts without expanding its build context.

The approved sample uses the exact synthetic UTF-8 source strings from
`tests/contracts/build_fixtures.py`: a tab, Greek alpha, an astral emoji, CRLF/LF,
and `helper()`. They are coordinate examples, not compilable Java or real tool
results. Source text is never executed. The UI checks actual file SHA-256,
manifest/snapshot identity and range bounds before displaying a highlight.
Columns are 1-based Unicode scalars with exclusive ends; the Monaco boundary
explicitly converts to UTF-16 columns. Multiple locations remain independently
addressable, including two ranges in the same file. No unresolved range is guessed.

Scenarios:

- **Approved API sample:** the unchanged two-finding result and approved source bytes.
- **UI coverage cases:** copies of the approved sample with clearly synthetic
  quality, duplicate, baseline and unresolved cases added in memory. The approved
  records/files remain unchanged; this extension is not separately claimed approved.
- **Unavailable baseline:** a synthetic unavailable baseline disables all choices.
- **Stale-selection error:** the approved error code clears prior choices and offers
  a fresh fixture load.

Schema shape checks are supplemented by UI guards for consumed source/evidence
bindings, duplicate IDs, current/open quality classification, independent verified
evidence, passing nonempty/unskipped baseline, protected inputs and valid locations.
These guards support this fixture UI; they do not replace the backend's complete
graph validation, authentication, redaction, ownership or approval policy.

The choice preview is a local draft of selected stable IDs and source scope. It
never fabricates a new approval reference or fingerprint. The approved selection
example is checked for schema/scope compatibility, not replayed as a new user
decision. Choices are cleared on fixture reload/change/error, and stale async
responses are ignored. Category/search filters preserve choices in the current
snapshot. A Monaco load failure keeps an exact highlighted read-only text fallback.

## Dependencies and limits

Monaco and Ajv supply the editor and actual JSON Schema 2020-12 validation.
`json-schema-to-typescript` generates types from the approved registry; jsdom
supports interaction tests with the existing React/Vitest stack. Versions and
transitive packages are locked. DOMPurify is pinned through an explicit override
to 3.4.18 because Monaco's declared transitive version was flagged by npm audit.
The resulting dependency audit reported zero known vulnerabilities at verification;
that is not a guarantee of full security.

The lazy Monaco chunk is approximately 2.62 MB before compression (about 672 KB
gzip), and Vite reports its normal size warning. No warning threshold was raised.
No syntax-analysis, provider, sandbox, model, upload, Gate 2, or backend capability
is claimed by this UI. Native macOS/M3 and real API integration were not tested.

See [contract semantics](../docs/contracts/SEMANTICS.md) and the current
[project status](../docs/PROJECT_STATUS.md). Publication, task acceptance and
merge remain separate from local verification.
