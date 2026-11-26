# Consumer compatibility — technical expectations

These expectations derive from the approved SRS/architecture and Issue #11.
They do not claim personal approval from Taha, Burkay or Alperen and do not assign
new tasks. The candidate wire version is 1.0.0 and remains subject to human review.

| Consumer | Required behavior | Shared fixture / verification |
|---|---|---|
| Taha — frontend/UI | Preserve typed stable IDs and source snapshot binding; render separate quality/security/baseline categories, eligibility and unknown/error states. Convert scalar columns to Monaco's coordinate model explicitly. Show separate execution/build/test/behavior/quality/security outcomes. Display immutable Gate 1 choices, patch/diff hashes and validation references; do not treat APPLICABLE or OK as user approval. | [API result](examples/result.json), [selection](examples/issue-selection.json), [safe stale-selection error](examples/error.json); model/graph/API tests |
| Burkay — adapters | Route by component and exact language. Declare parse/symbol/quality/dependency/build/test/coverage/safe_patch/security independently; missing tools remain unavailable or unresolved. Retain toolchain versions, confidence, symbol/source references, dependency uncertainty and evidence. Run the operation guard before execution and the proper sandbox for dynamic operations. | [Seven-language fixture](../../tests/contracts/fixtures/seven-languages.json), [LanguageAdapter interface](../../backend/core/schemas/adapter.py); unsupported-operation and supported-parser-only guard tests |
| Alperen — context/refactoring | Verify selected source/snapshot against the current trusted baseline; reject stale/security-only/broken-baseline selection. Keep complete context within measured budget and explicitly report omissions/effects/dependency uncertainty. Validate PatchCandidate with independent current PatchPolicy; preserve attempts/provenance and require validation of actual candidate bytes. Keep individual and final combined validation separate. | [Core graph](../../tests/contracts/fixtures/core.json), context/patch/validation classes; stale/scope/denominator/byte-binding/protected-file tests |

## Implemented versus planned

Implemented locally: strict models, recognized schema export, reference/metadata
validators, coordinate-byte checks, pure operation guard, API design description,
field dictionary, synthetic examples and automated checks.

CONTRACT_DEFINED: all seven language interfaces and the four documented API route
candidates. The committed capability fixture reports every operation as
NOT_IMPLEMENTED. This task does not report a parser, test runner, safe patcher,
coverage tool or security adapter as working.

RUNTIME_IMPLEMENTED requires future evidence from the actual integration. A
synthetic unit-test payload deliberately exercising SUPPORTED does not count.
Real local Qwen3-Coder 30B-A3B (ADR 0007) remains mandatory P0, with actual model/revision/settings
unknown until measured by its own task. No model was installed or invoked here.
Provider settings and budgets need actual authorization; no paid API is required
by these contracts.

## Integration decisions for human review

- Approve the exact version, scalar-coordinate convention, JCS fingerprints,
  typed-ID/source-snapshot semantics and strict unknown-field policy before
  independent consumers integrate them. Those are concrete candidate decisions
  in [SEMANTICS.md](SEMANTICS.md), not already obtained team sign-offs.
- The OpenAPI routes are a bounded candidate interface, not a running server or
  proof that authentication/idempotency/state/storage are implemented. Responses
  include reference closure for gate validation; runtime pagination must preserve
  a consistent immutable snapshot and trusted resolver before changing this rule.
- Future API/adapters may consume individual structural records, but approval and
  patch gates must supply complete referenced evidence plus independent trusted
  baseline state. Schema validation cannot authenticate arbitrary evidence claims.
- Artifact byte verification, actual tool receipts, redaction/egress consents,
  filesystem containment/symlink checks and sandbox operation belong to the later
  modules. No data-only VALIDATION result authorizes execution or final publication.
