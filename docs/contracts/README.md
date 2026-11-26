# F02-CONTRACT 1.0.0

Status: **CONTRACT_DEFINED**, local implementation prepared for human review.
This package supplies data contracts, pure validation and fixtures. Runtime
adapters, HTTP services, approval persistence, context extraction, patch generation,
sandbox execution, model integration and deployment are not implemented here.

The authoritative types are [Pydantic models](../../backend/core/schemas/models.py).
Their deterministic [JSON Schema Draft 2020-12 export](../../backend/core/schemas/cir-1.0.0.schema.json)
and [OpenAPI 3.1.1 description](openapi-1.0.0.json) share one definition registry.
There is no independently maintained second set of CIR types.

| Deliverable | Artifact |
|---|---|
| Nine FR-007 entities, capability/selection/context and API envelopes | [Models](../../backend/core/schemas/models.py), [data dictionary](DATA-DICTIONARY.md) |
| Closed-graph/reference and trusted-policy validation | [Validation](../../backend/core/schemas/validation.py), [semantics](SEMANTICS.md) |
| LanguageAdapter interface and operation precondition | [Adapter protocol](../../backend/core/schemas/adapter.py) |
| Source-coordinate convention and actual-byte bound check | [Coordinates](../../backend/core/schemas/coordinates.py) |
| UI/context/patch example graph | [Core fixture](../../tests/contracts/fixtures/core.json), [API example](examples/result.json) |
| Seven-language declaration, with no false implementation claims | [Adapter fixture](../../tests/contracts/fixtures/seven-languages.json) |
| Invalid examples | [21 deterministic invalid recipes](../../tests/contracts/fixtures/invalid-cases.json) and [graph tests](../../tests/contracts/test_contract_graph.py) |
| Compatibility and consumer expectations | [Semantics/versioning](SEMANTICS.md), [consumers](CONSUMERS.md) |
| Requirements and local evidence | [Traceability](TRACEABILITY.md), [task report](F02-REPORT.md) |
| Real CI check | [contract-checks workflow](../../.github/workflows/contract-checks.yml) |

All example bundles are explicitly `mode: FIXTURE`. Their tool versions, source
revisions, hashes and measurements are synthetic values for interoperability
tests, not claims that tools, a provider or the local security LLM ran. The seven adapter
declarations all use CONTRACT_DEFINED/NOT_IMPLEMENTED. The one supported-parser
state constructed in a unit test tests the guard's data semantics only.

## Run locally

Use Python 3.12.14, matching the pinned CI runtime, in an environment outside the
checkout. Python 3.11+ is the implementation minimum; other versions need their
own verification. Install the complete pinned dependency tree:

```text
python -m pip install -r tests/contracts/requirements.txt
python -B tests/contracts/run_checks.py
python -B -m unittest discover -s tests/contracts -v
python -B -m backend.core.schemas.export --check
```

The CI entry point requires the real model/graph/API suites, fixture inventory,
nonzero discovery and essential acceptance cases. Skips and failing exits cannot
satisfy the job. Raw unittest discovery also executes the complete current suite;
use the guarded entry point for acceptance automation.

For intentional contract edits, regenerate the exports and examples, then review
the diff and rerun checks:

```text
python -B tests/contracts/build_fixtures.py
python -B -m backend.core.schemas.export
python -B tests/contracts/run_checks.py
```

Runtime dependencies are Pydantic (already selected by the approved architecture)
and the small RFC 8785 implementation for cross-language stable fingerprints.
Tests additionally use jsonschema for independent validation and the vendored,
byte-pinned official OpenAPI schema. Versions of direct and transitive packages
are pinned in the two scoped requirements files. No database, queue, server,
paid API, toolchain installation or model execution is introduced.

## Consume safely

1. Validate a single entity's structural shape with its model or exported schema.
2. For a gate, assemble its closed reference graph and call `validate_bundle`.
   Structural JSON Schema validation alone is insufficient for source ranges,
   evidence status, references and trusted-policy constraints.
3. Supply `PatchPolicy` from independently trusted current scope, baseline file
   metadata, frozen test suites and authorized file paths. Never construct this
   policy from an untrusted patch/API request. Eligible Gate 1 selections and
   candidate validation require that trusted baseline context.
4. Resolve/authorize opaque artifacts separately, verify their actual bytes and
   tool receipts, and enforce redaction/sandbox/consent limits before execution.
   This package validates contracts; it cannot authenticate arbitrary producer
   claims or inspect artifact bytes that have not been supplied.

The adapter operation guard rejects FIXTURE mode even if a caller changes a
capability declaration. Actual execution must use trusted INTERCHANGE data and
the future runtime's authorization and sandbox controls.

```python
from backend.core.schemas import validate_bundle
from backend.core.schemas.validation import PatchPolicy

# These values come from the trusted source/consent/artifact registries.
policy = PatchPolicy(expected_scope=current_scope, allowed_paths=("src/",),
                     expected_files=baseline_files, expected_test_suites=frozen_suites)
bundle = validate_bundle(request_payload, patch_policy=policy)
```

This boundary supplies interoperable contracts for later modules. Human review,
exact-revision publication authorization, hosted CI and canonical acceptance remain
separate from local validation. See the [report](F02-REPORT.md) for actual results.
