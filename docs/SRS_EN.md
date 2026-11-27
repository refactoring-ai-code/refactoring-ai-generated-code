# Software Requirements Specification (SRS)
# Secure Refactoring and Quality Improvement of AI-Generated Code

> **Current-decision precedence:** Earlier draft and transition
> statements are historical records. The approved SRS v0.4.0,
> its 2026-11-25 v0.4.1 amendment (ADR 0007) and subsequently
> approved scope decisions take precedence.
> Current GitHub task, PR and dependency states must always
> be independently verified against live repository evidence.

**Document:** RAGC-SRS-001 · **Version:** 0.4.1 · **Date:** 2026-10-27  
**Status:** APPROVED SRS — v0.4.0 approved by Burkay Çakar on 2026-10-27; the v0.4.1 amendment (local security model, cloud refactoring LLMs, approval authority) was recorded by the project owner on 2026-11-25 in [ADR 0007](DECISIONS/0007-local-llm-and-approval-authority.md); product verification remains separate.  
**Product:** Refactoring AI-Generated Code — Engineering Design II, Group B  
**Target delivery:** 2027-01-01 (exact local submission time UNKNOWN)  
**Authority:** Owner-supplied `01_Master_Sistem_Mimarisi.pdf` v2.0 → `02_Adim_Adim_Gelistirme_Rehberi.pdf` v2.0 → modular presentation + 2026-10-20 image → associated live GitHub requirement and issue records. Older `01_System_Operation_and_Architecture.pdf` and `03_Technical_System_Presentation_Revised.pdf` are secondary historical documents.  
**Execution governance:** owner decisions dated 2026-10-26, 2026-10-27 and 2026-11-25 (ADR 0007); approvals follow the GitHub development workflow (protocol v3) with no single final approver.  
**Language equivalent:** [SRS.md](SRS.md), same stable FR/NFR IDs. The source PDFs were owner-provided artifacts and MUST NOT be assumed present inside the public repo.

> This specifies an intended system; it does not claim that a requirement, integration, security claim, benchmark, deployment or research outcome is already VERIFIED.

## 1. Purpose, stakeholder roles and system boundary

The product receives authorized AI-generated or other source code as ZIP, folder or snippet; creates an immutable original V0 and per-component language capabilities; runs three evidence-bearing baseline branches (quality, deterministic security with local model commentary, and isolated initial build/test/coverage); offers users two separate acceptance points; generates targeted LLM patch proposals with bounded context and conflict-aware scheduling; validates each patch in isolation; composes selected verified patches on a *new V0 clone* and reruns every mandatory combined check; then produces measured before/after comparisons, a validated final ZIP, HTML/PDF outputs and accessible history.

**Actors:** code owner/user (two product decisions and input/cloud/execution consents); application operator; research evaluator; language analysis adapters; sandbox/build/test workers; authorized cloud patch providers; local Qwen3-Coder security review; developer/Codex/orchestrator (development responsibilities only).

**Included:** safe input and evidence provenance, language adapter framework, real Java/Python/JavaScript/TypeScript/C#/Go/C++ capabilities, security scanner and mandatory local Qwen3-Coder 30B-A3B review, deterministic validation, approval UX, bounded LLM calls, final ZIP/PDF/HTML/history and rigorous research protocol.

**Excluded unless separately approved:** automatic remediation of arbitrary security findings, broad bug fixing, replacement of a user's tests to obtain a pass, uncontrolled program rewrites, arbitrary network/code exfiltration, proof of complete behavior equivalence.

## 2. Approved target architecture, modules and technical contracts

| Module | Target technology / expected ownership within product | Release obligation |
|---|---|---|
| UI | React, TypeScript, Tailwind, Monaco, ECharts | Two real product approval gates, issue selection, diffs, measurements, history, exports |
| Core backend | Python, FastAPI, Pydantic | API/state machine/consent/access checks, orchestration and typed contracts |
| Queue/workers | Redis with RQ | Durable non-blocking jobs, retry/cancel, bounded concurrency |
| Metadata and immutable artifacts | SQLite, SQLAlchemy/Alembic; content-addressed artifact storage, optional S3 | Immutable V0, trusted test baselines, attempts, evidence, final versions and exports |
| CIR / Core Engine | Normalizers, evidence registry, correlator, eligibility policy, metric normalizer | Preserve raw evidence and uncertainty; do not confuse security vs quality vs test status |
| Java adapter | Java 21/Maven, JavaParser Symbol Solver, PMD, CPD, JUnit 5, JaCoCo | Working mandatory P0 pilot with actual build/test and controlled patch validation |
| Python adapter | ast/LibCST, Ruff/Pylint, pytest, coverage.py | **Mandatory first delivery (P0)** |
| JS/TS adapters | TS Compiler API/ts-morph, ESLint, tsc, Vitest/Jest and coverage | **Mandatory first delivery (P0)**; monorepo/component boundaries honored |
| Static security | Gitleaks, Semgrep, OSV Scanner | Real deterministic results and explicit incomplete/unavailable statuses |
| Local AI | Qwen3-Coder 30B-A3B target (ADR 0007); only the AST/SAST-paired security review runs locally, as an isolated service with checked model/quantization/memory/runtime compatibility (target hardware: NVIDIA DGX Spark / GB10) | **Mandatory first delivery (P0)**; no false readiness while unavailable |
| Cloud refactoring | Authorized DeepSeek/GLM/Qwen style provider adapters, bounded unified diffs | Real provider evidence, no paid/unconsented request |
| Context/scheduler | Symbol graph, side-effect/read-write analysis, conservative DAG | Serialize unknown conflicts, up to six genuinely independent jobs (ADR 0007) |
| Validation | Sandbox workers, per-language test/build/coverage/scanners | Candidate and complete combined validation, independent quality/behavior assessment |
| Reporting | Comparison engine, charts, artifact/history service, HTML/PDF | **Mandatory first delivery (P0)** |
| C# language adapter | Roslyn/.NET SDK, supported xUnit/NUnit/MSTest and coverage | **Mandatory P0 first delivery**, real build, source/symbol evidence and safe patch |
| Go language adapter | go/parser, go/types, go vet, go test/coverage and go module dependencies | **Mandatory P0 first delivery**, real build/test and safe patch |
| C++ language adapter | Clang/clang-tidy, compile_commands.json, existing CMake/CTest or supported equivalent | **Mandatory P0 first delivery**, native build/test and safe patch |

The exact dependency versions, model weight IDs, quantization/runtime and deployment hardware are **to be verified**, not inferred from the diagram. SonarQube may supplement PMD/CPD but is not required for the core Java build. A desktop M3 does not provide CUDA; access to a compatible discrete GPU is UNKNOWN.

## 3. End-to-end user workflow and immutable engineering invariants

1. **Safe intake:** validate ZIP/folder/snippet, manifest, consent, processing/retention limits; freeze exact V0 with hash.
2. **Language routing:** detect per-component languages, declare parser/scanner/test/coverage/safe_patch capabilities.
3. **Initial analysis:** actual quality findings, deterministic security evidence (+ local Qwen3-Coder commentary), and sandboxed baseline tests/coverage; keep each branch's errors explicit.
4. **Approval Gate 1:** show source-aligned issue explorer, category filters, eligible quality refactoring choices, immutable chosen-finding fingerprints.
5. **Bounded context:** target symbols, caller/callee edges, public interfaces, side effects, relevant tests and source restrictions; build conservative conflict DAG.
6. **Refactoring provider:** request narrow structured patch from authorized real provider, at most six evidence-independent jobs concurrently (ADR 0007).
7. **Individual validation:** build/typecheck/frozen regression, inspect target quality and new security risks; one initial candidate + at most two corrective attempts per task.
8. **Approval Gate 2:** human selects actually acceptable patch IDs based on diff/test/security evidence.
9. **Final composition and outputs:** apply only accepted patches on a clean V0 clone; full combined regression/security/static verification; durable final ZIP, HTML/PDF dashboards and analysis history.

**Invariants:** V0 and frozen test hashes never change; approvals represent different decisions; scanner findings do not become general refactoring authorization; model self-assertions are not evidence; build success is not behavioral equivalence; single-candidate success never replaces combined validation; no secret plaintext in model contexts, PDFs or public logs; failures remain in metrics.

## 4. State machine, result types and data contracts

**Normal workflow states:** UPLOADED → BASELINE_CREATED → LANGUAGE_ROUTED → ANALYZING → FINDINGS_READY → AWAITING_ISSUE_SELECTION → REFACTORING → VALIDATING_CANDIDATES → AWAITING_PATCH_APPROVAL → COMBINED_VALIDATION → FINALIZED → REPORT_READY.

**Alternative/terminal states:** BLOCKED_INPUT / BASELINE_FAILURE / UNVERIFIED / PATCH_FAILED / MERGE_CONFLICT / USER_CANCELLED. Each transition is validated server-side and persisted; worker restarts must not lose accepted decisions or double-schedule a job.

**Independent outcomes:** `behavior_status` is PASSED / FAILED / UNVERIFIED; `quality_outcome` is IMPROVED / UNCHANGED / WORSE / NOT_COMPARABLE. A clean report requires a completed scan, not an unavailable scanner. Security observations attributed only to Local AI remain LLM_SUSPECTED/UNCONFIRMED pending objective corroboration.

**Logical entities (not mandated one-table-per-object):** Project, ProjectVersion, FileManifest, ImmutableArtifact, SourceComponent, Capability, SourceLocation, Symbol, DependencyEdge, Finding, Evidence, Metric, ToolExecution, BaselineTestSuite, TestRun, CoverageRun, IssueSelection, ContextPackage, RefactorJob, Attempt, PatchCandidate, ValidationResult, PatchApproval, CombinedValidation, FinalExport, AuditEvent, Report. Preserve immutable IDs, hashes, actual tool/model revision, rule sets, UTC timestamps, actors, input/output linkages and error provenance.

**Representative contract routes are design candidates, not deployed endpoints:** `POST /api/projects`, `POST /api/projects/{id}/versions`, `POST /api/versions/{id}/analyze`, `GET /api/analyses/{id}/findings`, `POST /api/analyses/{id}/issue-selections`, `POST /api/refactoring-jobs`, `GET /api/refactoring-jobs/{id}`, `GET /api/patches/{id}/diff`, `POST /api/refactoring-jobs/{id}/approvals`, `POST /api/refactoring-jobs/{id}/finalize`, `GET /api/comparisons/{id}`, `POST /api/versions/{id}/reports`, `GET /api/projects/{id}/history`, `GET /api/jobs/{id}/events`, `GET /api/artifacts/{id}/download`. Final API shapes and state schemas belong in approved interface-contract tasks.

## 5. Functional requirements

P0 = mandatory first delivery; all FR-001–FR-062 requirements below are P0 under the explicit 2026-10-26 owner scope decision. Requirements are acceptance contracts, not claims of implementation. Existing issue IDs are traceability references.

| ID | Priority | Required observable behavior | Source issue(s) |
|---|---|---|---|
| FR-001 | P0 | Accept ZIP, folder and snippet inputs; produce a file manifest, content hashes, language detection and excluded-path rationale. | #13 |
| FR-002 | P0 | Reject archive traversal, symlinks, Unicode/path collisions, decompression bombs, excessive size and file counts. | #13 |
| FR-003 | P0 | Keep byte-identical immutable V0 and run analysis, patches and final composition only in isolated derivatives. | #9,#13,#29 |
| FR-004 | P0 | Record terms, retention, cloud transmission and dynamic execution consents separately with versions, actors and timestamps. | #13 |
| FR-005 | P0 | Enforce ownership/authorization for all projects, histories and artifact downloads. | #13,#31 |
| FR-006 | P0 | Persist versions, jobs, approvals, attempts and state transitions; reject invalid transitions and replayed/duplicate mutations. | #12 |
| FR-007 | P0 | Version CIR contracts for Finding, Evidence, SourceLocation, Symbol, DependencyEdge, Metric, TestResult, PatchCandidate and ValidationResult. | #11 |
| FR-008 | P0 | Route language per file/component even when the user selects a language; never silently parse unknown files with the wrong adapter. | #14 |
| FR-009 | P0 | Record a real Java 21/Maven AI-generated working V0 pilot with original prompts, models, attempts, fixed tests and hashes. | #9 |
| FR-010 | P0 | Extract Java symbols, overloads, source ranges and uncertain references through JavaParser Symbol Solver using observed evidence. | #14 |
| FR-011 | P0 | Declare LanguageAdapter parse, quality, dependency, test, coverage and safe_patch capabilities independently with confidence. | #14 |
| FR-012 | P0 | Normalize genuine PMD/CPD quality findings for at least four meaningful categories, preserving rule/version/file/line evidence. | #15 |
| FR-013 | P0 | Ensure Java P0 PMD/CPD works without SonarQube; when enabled, isolate SonarQube's external service/database. | #15 |
| FR-014 | P0 | Correlate and normalize multiple analyzer findings while retaining independent source evidence and provenance. | #15 |
| FR-015 | P0 | Run actual Gitleaks, Semgrep and OSV scanning on supported scopes; expose coverage and unavailable checks. | #18 |
| FR-016 | P0 | Redact secrets from findings, prompts, UI, logs and PDF; do not present speculative LLM findings as confirmed security issues. | #18,#20 |
| FR-017 | P0 | Keep security findings in SECURITY_REVIEW; deny ordinary QUALITY_REFACTOR eligibility to them. | #18,#21 |
| FR-018 | P0 | Execute untrusted builds/tests only in isolated, non-root workers with default-deny networking and resource limits. | #16 |
| FR-019 | P0 | Fail closed if the sandbox is unavailable/unsafe; prevent host secrets, Docker socket and host path access. | #16 |
| FR-020 | P0 | Run V0 Java JUnit/JaCoCo discovery and coverage; retain stable test IDs, suite hashes and environment fingerprints. | #17 |
| FR-021 | P0 | When tests are missing, attempt characterization based on real observed V0 behavior in an isolated copy; freeze only passing V0 tests. | #17 |
| FR-022 | P0 | Report missing tests, broken baseline, missing environment and introduced regressions separately; build-only success is not behavioral PASS. | #17 |
| FR-023 | P0 | Provide Monaco Issue Explorer filters for Quality, Complexity, Duplication, Security and Baseline with actual source highlights. | #21 |
| FR-024 | P0 | Show both duplicate source locations; label uncertainty, disabled/error states and fixture/mock UI modes explicitly. | #21 |
| FR-025 | P0 | Record Approval Gate 1 with immutable V0, analysis_id and selected eligible issue fingerprints. | #22 |
| FR-026 | P0 | Reject security/ineligible choices and broken-baseline bypass server-side; make repeated submissions idempotent. | #22 |
| FR-027 | P0 | Generate bounded, redacted ContextPackages from symbols, callers/callees, tests, models, effects and public interfaces. | #23 |
| FR-028 | P0 | On context-budget overflow, never silently discard critical dependencies; narrow safely, ask for context or stop. | #23 |
| FR-029 | P0 | Construct a conservative conflict DAG from read/write sets and unknown shared contracts; serialize conflicts. | #24 |
| FR-030 | P0 | Allow at most six evidence-independent jobs in parallel (ADR 0007), each with separate workspace and immutable input hash. | #24 |
| FR-031 | P0 | Obtain schema-valid unified diffs and explanations from an authorized real patch provider, enforce path/scope allowlists. | #25 |
| FR-032 | P0 | Require approval of provider egress, source permissions, API quota and charges before uploading sensitive code or making paid calls. | #25 |
| FR-033 | P0 | Reject patches that modify protected tests, rule configurations, V0 or disallowed paths. | #25 |
| FR-034 | P0 | Validate every patch candidate with syntax/build, frozen regression, target finding, coverage and security checks. | #26 |
| FR-035 | P0 | Store behavior_status and quality_outcome independently; expose new risks and unresolved findings. | #26 |
| FR-036 | P0 | Enforce one initial attempt plus at most two correction attempts; separate transport retry and persist budgets across restarts. | #27 |
| FR-037 | P0 | Review all patch hunks, attempts, model/source attribution and verification evidence with Monaco Diff. | #28 |
| FR-038 | P0 | At Approval Gate 2 allow only eligible validated patch IDs; FAILED/UNVERIFIED cannot enter the normal validated final. | #28 |
| FR-039 | P0 | Apply approved patches deterministically on a fresh V0 clone and rerun complete regression/static/security after composition. | #29 |
| FR-040 | P0 | Never publish a VALIDATED final ZIP until every mandatory combined validation gate succeeds. | #29 |
| FR-041 | P0 | Enable owner-protected re-download of final ZIP, HTML/PDF, history and linked original/final version records. | #29,#30,#31 |
| FR-042 | P0 | Compute before/after findings, complexity, duplication and coverage with the same rules, tools and scope; mark incomparable outputs. | #30 |
| FR-043 | P0 | Report zero-denominator as N/A, distinguish percent versus percentage points, and retain failures/new findings. | #30 |
| FR-044 | P0 | Derive HTML and PDF from the same measured run and evidence references; redact secrets and prohibit invented AI explanations. | #30,#31 |
| FR-045 | P0 | Demonstrate real upload → analysis → Approval 1 → patch → candidate validation → Approval 2 → combined validation → ZIP for each of seven mandatory Java/Python/JS/TS/C#/Go/C++ languages. Missing capabilities BLOCK the release. | #35,#40–#42 |
| FR-046 | P0 | Verify negative E2E cases for broken baseline, no tests, provider timeouts, conflict, secret leakage and combined regressions. | #35 |
| FR-047 | P0 | Use a fixed research dataset of at least 12 tasks and include unsuccessful attempts in all appropriate denominators. | #8,#36 |
| FR-048 | P0 | Compare sequential versus parallel execution in three matched repetitions with constant context/tests/rules and measured time/token cost. | #36 |
| FR-049 | P0 | Measure ≥50% finding-reduction as an experimental target, never claim achievement or formal equivalence in advance. | #36 |
| FR-050 | P0 | Deliver reproducible V0/V1 hashes, generation prompts, real test evidence, working setup/demo and documented limitations. | #37 |
| FR-051 | P0 | Deliver a working Python AST/LibCST, Ruff/Pylint and pytest/coverage adapter with safe-patch validation without breaking Java. | #32 |
| FR-052 | P0 | Deliver JS/TS adapters using TS Compiler API, ESLint, tsc, Jest/Vitest and coverage with actual verified capabilities. | #33 |
| FR-053 | P0 | Support mixed Java/Python/JS/TS/C#/Go/C++ projects with per-component metrics/tests, honest cross-service uncertainty and language-specific verification. | #34,#40–#42 |
| FR-054 | P0 | Integrate a real Qwen3-Coder 30B-A3B review service after validating exact model/revision, quantization, GPU/runtime, VRAM and latency. | #19 |
| FR-055 | P0 | Return redacted, evidence-linked UNCONFIRMED Qwen3-Coder commentary; deterministic SAST continues when local AI fails. | #20 |
| FR-056 | P0 | Evaluate Qwen3-Coder against independently labeled examples, including precision/recall and complete FP/FN denominators. | #20 |
| FR-057 | P0 | Provide detailed AI-assisted PDF/HTML reports with numeric parity, backend-derived metrics and evidence-based narration. | #31 |
| FR-058 | P0 | Implement a working C#/Roslyn adapter with symbol/source-range analysis, real .NET build, supported xUnit/NUnit/MSTest and coverage, evidence-backed quality checks, scoped patch and sandbox verification; report missing SDK honestly. | #40 |
| FR-059 | P0 | Implement a working Go adapter with module/workspace-aware parser/type analysis, go vet or applicable quality rules, real go test/coverage and dependency-aware scoped patch validation. | #41 |
| FR-060 | P0 | Implement a working C++/Clang adapter with AST/source locations, compile_commands-aware context, clang-tidy, real CMake/CTest or supported project build/test/coverage, isolated scoped patch validation; missing build context is UNVERIFIED. | #42 |
| FR-061 | P0 | Produce real positive and negative validation evidence for all seven mandatory language adapters, mixed-project capability, immutable V0/frozen tests and trustworthy export/report results. | #34,#35,#40–#42 |
| FR-062 | P0 | Gate first-delivery acceptance on seven VERIFIED language patch capabilities together with Qwen3-Coder, HTML/PDF/ZIP and all required security validation. No missing adapter may be silently deferred. | #35,#37,#40–#42 |

## 6. Non-functional requirements

| ID | Priority | Risk/quality constraint and verification | Source |
|---|---|---|---|
| NFR-01 | P0 | Isolate untrusted execution using non-root identity, default-deny network, CPU/RAM/time/process limits, denied secrets, and adversarial fixtures. | #13,#16 |
| NFR-02 | P0 | Verify SHA-256 integrity of V0 original bytes and frozen tests at every relevant stage. | #9,#13,#29 |
| NFR-03 | P0 | Enforce owners/permissions, distinct consents, external API redaction and retention/deletion policy. | #13,#18,#31 |
| NFR-04 | P0 | Record tool, ruleset, config, coverage scope, suite and environment fingerprints for comparable/reproducible results. | #15,#17,#30 |
| NFR-05 | P0 | Never promote NOT_RUN to PASS or fake provider results; missing scans cannot be reported as clean. | #26,#35 |
| NFR-06 | P0 | Handle worker restart, cancellation, idempotent retries and avoidance of duplicate mutations. | #12,#24 |
| NFR-07 | P0 | Use versioned frontend/backend API schemas and accurate per-adapter capabilities and error states. | #11,#21 |
| NFR-08 | P0 | Provide actual repeatable clean-checkout setup with working backend/frontend/queue/database build/test commands. | #10 |
| NFR-09 | P0 | Use minimum sufficient complexity; prohibit unjustified new frameworks, class hierarchies, infrastructure and test proliferation. | Genesis v2 |
| NFR-10 | P0 | Report correct metric units/formulas, never silently equate Sonar/CPD or unrelated coverage denominators. | #15,#30 |
| NFR-11 | P0 | Never expose API keys in browser/repository; untrusted source comments cannot override execution instructions. | #18,#25 |
| NFR-12 | P0 | Persist run/attempt/approval/final UTC audit and history without leaking source or credentials in logs. | #12,#30 |
| NFR-13 | P0 | Support hardware/model/research claims only with real measurements, limitations and configurations. | #19,#36 |
| NFR-14 | P0 | All seven mandatory adapters expose individual capabilities/confidence/coverage without regressing other language workflows. | #32–#34,#40–#42 |
| NFR-15 | P0 | Do not claim public deployment without verified isolation, threat model, deployment configuration and release decision. | Architecture v2 §16 |
| NFR-16 | P0 | Verify actual installability, licensing, OS/runtime constraints and reproducible tool versions for JDK, Python, Node/TypeScript, .NET SDK, Go, Clang/native build and Qwen3-Coder service. | #10,#19,#40–#42 |
| NFR-17 | P0 | Execute native, .NET and Go builds/tests only in resource-limited sandboxes; expose C++ ABI/compile database assumptions, Go module dependencies and .NET restore egress restrictions. | #16,#35,#40–#42 |

## 7. Measurable acceptance matrix and release gates

| Scenario | Evidence and pass expectation |
|---|---|
| Malicious archive, symlink or decompression attack | Rejected; no traversal/host impact, V0 remains unchanged |
| Working Java 21/Maven pilot | Real parser, PMD/CPD, JUnit/JaCoCo results, source/rule/tool/coverage references |
| Python, JavaScript and TypeScript adapter flows | Real parse, quality, test, coverage and supported patch validation with independent capability flags |
| Mixed React + Python ZIP | Same run analyzed by distinct adapters; per-component results without fictitious full cross-service verification |
| Sandbox runaway/untrusted access | Resource-limited isolation and no host secret/network access |
| Missing tests or broken baseline | Correct UNVERIFIED/BASELINE_FAILURE; no normal validated final export |
| Scanner offline, malicious secret or fake Local AI line | Masking, explicit INCOMPLETE, rejection of fabricated evidence references |
| Local Qwen3-Coder 30B-A3B service | Recorded exact model/version/runtime/quantization/VRAM/latency and independent labeled evaluation |
| Approval 1 bypass/security issue selection | Server rejects invalid choices; saved immutable selected issue snapshot |
| Unknown conflict and genuinely independent jobs | Conflicting jobs serialized; up to 6 independent jobs concurrently (ADR 0007) |
| Invalid patch / test-file change | Rejected before downstream validation |
| Patch correction budget | Initial + at most 2 correction attempts persisted |
| Individually passing but jointly broken | Combined validation FAILED, no VALIDATED final ZIP |
| Genuine two-approval product path | Only approved patch IDs enter fresh V0 composition; all combined gates pass |
| HTML/PDF/ZIP/history | Same evidence/run numbers, user authorization, complete redact/re-download paths |
| Research dataset and repeated trials | At least 12 frozen tasks, 3 matched repeats per condition, failed attempts in denominators |

A passing governance test or a successful Git push is *not* product acceptance. All mandatory paths require task-specific test evidence and a separate risk-based release decision. Delivery cannot be declared ready while any of the seven mandatory language adapters, Qwen3-Coder, PDF/HTML or secure sandbox requirements remain unverified.

## 8. Traceability to existing GitHub plans (do not delete planning history)

| Plan / existing issue | Covered requirements |
|---|---|
| F00-PLAN #8; F00-V0 #9 | FR-009, FR-047–050 |
| F01-GOV #1; F01-ENV #10 | Governance, NFR-08 |
| F02-CONTRACT #11; F02-STATE #12 | FR-006–007, versioned schemas and state |
| F03-INPUT #13 | FR-001–005 |
| F04-JAVA #14; F05-QUALITY #15 | FR-008–014 |
| F06-SANDBOX #16; F06-TESTS #17 | FR-018–022 |
| F07A-SCAN #18; F07B-PILOT #19; F07B-LOCAL #20 | FR-015–017, FR-054–056 |
| F08-UI #21; F08-INTEGRATE #22 | FR-023–026 |
| F09-CONTEXT #23; F09-SCHED #24 | FR-027–030 |
| F10-PATCH #25; F11-VALIDATE #26; F11-RETRY #27 | FR-031–036 |
| F12-REVIEW #28; F12-FINAL #29 | FR-037–040 |
| F13-BASIC #30; F13-ADV #31 | FR-041–044, FR-057 |
| F14-PY #32; F14-JSTS #33; F14-MIX #34 | FR-051–053, FR-061 | 
| F14-CS #40; F14-GO #41; F14-CPP #42 | FR-058–062, NFR-16–17 |
| F15-P0 #35; F15-EXPERIMENT #36; F15-HANDIN #37 | FR-045–050, FR-061–062 |

**Priority promotion:** #19, #20, #31, #32, #33 and #34 were originally P1 in the GitHub task registry; explicit owner approval on 2026-10-26 promotes them to P0. The 31 technical issues, six research work packages and verified dependency graph must remain intact, while fixed personal implementation assignments migrate to sequential task ownership only after compatible gate, test, live issue and PR updates. No implementation success is inferred from this reclassification.

## 9. Project Genesis v2.0 implementation governance (distinct from product approval)

- **GOV-001:** The authorized five: Burkay (@cakarburkayy), Cafer (@caferkilinc), Alperen Enes Yaman (@Yaman-A-E), İsmail (@ismail-cevik), Uğur = Taha Uğur Toyran (@tahaugurtoyran).
- **GOV-002:** Exactly one active implementation owner; invariant cyclic order Burkay → Cafer → Alperen → İsmail → Uğur → repeat. No skipped turn without the project owner's explicitly recorded exception.
- **GOV-003:** `main` is the approved accepted integration branch. Numbered feature PR branches remain available for independent review; they do not confer concurrent implementation ownership.
- **GOV-004:** PR #38 was made before Genesis activation and is **not** a completed Genesis rotation. It was merged with explicit owner authorization on 2026-10-27 (`5754ed6`) and consumed no rotation turn.
- **GOV-005:** Preserve all 31 technical issues and dependencies. Remove fixed future assignee/primary/support/reviewer assignments after compatibility migration; assign the current implementation owner only through canonical state, not preassigned issue backlog.
- **GOV-006:** Orchestrator assigns one bounded task → Codex inspects, edits, verifies, reports and stops → human reviews, commits and pushes → orchestrator verifies handoff/evidence → exactly one rotation advances on acceptance; duplicate (task, SHA) cannot count twice.
- **GOV-007:** Maintain minimal permanent AGENTS.md, a proven-compatible development-handoff skill, current report and roadmap/state/history records; reuse existing equivalents, avoid parallel sources of truth.
- **GOV-008:** Approvals follow the GitHub development workflow (protocol v3): normal repository permissions, the required PR reviews and successful technical CI. The single-final-approver rule (ADR 0004) and the `GENESIS-OWNER-APPROVED` marker are retired by ADR 0007. The project owner records consequential scope, architecture, security-boundary and release decisions as ADRs; real CI and handoff evidence remain mandatory.

## 10. Controlled decisions, implementation blockers and document approval

| ID | Decision, evidence or unresolved constraint |
|---|---|
| DEC-001 | Supplied 2026 v2.0 Master Architecture and Step-by-Step Guide override conflicting historical v1 PDF and presentation claims. |
| DEC-002 | Due 2027-01-01; submission time/channel UNKNOWN. |
| DEC-003 | Fixed team assignments are superseded by rotating single developer; actual registry/gate and issue migration is staged to avoid bypassing review. |
| DEC-004 | PR #38 could not merge solely because its governance CI checks passed; it was merged on 2026-10-27 (`5754ed6`) after the separate owner merge decision. |
| DEC-005 | Java may implement first, but Python, JS/TS, C#, Go, C++, mixed-component validation and local Qwen3-Coder are mandatory **in the same first delivery**. |
| DEC-006 | Qwen3-Coder 30B-A3B (ADR 0007) exact weights, quantization, compatible hardware/runtime and latency remain unverified; access to an M3 is not CUDA. Refactoring LLMs run with authorized cloud providers. |
| DEC-007 | HTML/PDF and history must use real evidence and consistent numbers, not an optional mock final. |
| DEC-008 | Actual patch provider model, privacy/egress consent, quota and spending authorization UNKNOWN; not permission to incur costs. |
| DEC-009 | Local academic demonstration versus internet-facing multi-user deployment requires a distinct threat/deployment approval. |

This document is the approved SRS v0.4.1: both v0.4.0 language versions were approved by the owner on 2026-10-27 (§12) and the v0.4.1 amendment was recorded on 2026-11-25 by ADR 0007. Record deviations via scoped change request/ADR; keep stable FR/NFR IDs and version increments without rewriting unrelated historic task metadata.

## 11. DEC-010 — 2026-10-27 owner-approved seven-language mandatory scope

The owner's latest explicit scope makes **C#, Go and C++ working adapters mandatory P0 for the same first delivery** as Java, Python, JavaScript, TypeScript and local Falcon-Mamba 7B. This supersedes any historical `future adapter` or P1 wording. New stable task IDs F14-CS (issue #40), F14-GO (#41) and F14-CPP (#42) are approved planning work. Each requires accepted F02-CONTRACT, F06-SANDBOX and F11-VALIDATE; mixed adapter acceptance F14-MIX (#34) requires all three plus Python/JS/TS. F15-P0 (#35) additionally requires F14-MIX, F07B-LOCAL (#20) and F13-ADV (#31) before it may pass first-delivery verification. *(2026-11-25: the local security model was changed to Qwen3-Coder 30B-A3B by ADR 0007.)*

Three live GitHub issues exist without fixed assignees. Existing 31 tasks / 54 native edges were not destroyed; new native subissue and prerequisite links remain **PENDING_SAFE_MIGRATION** until independently reviewed policy activation. PR #38 remains OPEN, and no separate merge authorization has been granted. Burkay is the owner-designated technical lead and audit coordinator for PR #38; independent review still requires a non-contributor, non-author reviewer under the existing governance controls. This SRS and the Turkish v0.4 counterpart remain **REVIEW DRAFT** until dual-language final sign-off. *(Later state: the native links were verified by Actions run 40518968864; PR #38 was merged on 2026-10-27 at `5754ed6`; both SRS versions were approved the same day, see §12.)*

## 12. Final owner SRS approval — 27 October 2026

**APPROVED_BY:** Burkay Çakar (@cakarburkayy). Both complete SRS v0.4.0 translations, FR-001–062 and NFR-01–17, are approved. Seven working language adapters (including C#, Go and C++) and real Falcon-Mamba 7B are mandatory P0 first delivery. Burkay is the sole required final approver; peer reviews are optional. Each future PR approval is bound to its HEAD SHA while actual CI, dependency, security and handoff verification remain mandatory. PR #38 was merged at `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c`. Approved requirements are not verified running software.

**AMENDMENT — v0.4.1 (2026-11-25, [ADR 0007](DECISIONS/0007-local-llm-and-approval-authority.md)):** The project owner recorded these decisions: (1) the mandatory P0 local security review model is **Qwen3-Coder 30B-A3B**, replacing Falcon-Mamba 7B; current requirement lines are updated, dated decision paragraphs and the sign-off above are kept and annotated, and the earlier wording remains in Git history. (2) Only the AST/SAST-paired security LLM runs locally; refactoring/patch LLMs run with authorized cloud providers on masked, bounded context (FR-016 and FR-032 unchanged). (3) The "sole required final approver" rule above and the HEAD-bound Burkay approval are retired; approvals follow the protocol v3 GitHub workflow (GOV-008). (4) The limit for concurrently running verified-independent refactoring jobs is raised from three to six (FR-030); conflicting or unknown relationships still run one after another. FR/NFR identifiers, P0 priorities, the seven-language scope and both in-product approval gates are unchanged; only the parallelism limit in FR-030 is updated.
