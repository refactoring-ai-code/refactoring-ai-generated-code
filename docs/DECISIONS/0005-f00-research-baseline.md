# ADR 0005 — F00 research baseline and evidence protocol

**Date:** 2026-11-02 (Europe/Istanbul)<br>
**Task / owner:** F00-PLAN / #8 / Burkay Çakar (@cakarburkayy)<br>
**Status:** Protocol prepared for owner review; dataset **NOT_FROZEN**; experiments **NOT_RUN**. This document does not attest implementation or accepted handoff.<br>
**Amended:** 2026-11-25 by [ADR 0007](0007-local-llm-and-approval-authority.md) — approvals assigned to Burkay below (e.g. dataset freeze) are recorded by the project owner through the v3 GitHub workflow; the local model under evaluation is Qwen3-Coder 30B-A3B.<br>
**Inspected baseline:** `67233482f2d10462933328c4b162d150bb4b0993`, accepted integration branch `main`; local task branch `docs/8-freeze-evidence-protocol`.

## 1. Authority, scope and existing evidence

Use the approved [TR SRS](../SRS.md) and [EN SRS](../SRS_EN.md) v0.4.0, [architecture](../ARCHITECTURE.md), [task registry](../../.github/task-plan.json), [roadmap](../DEVELOPMENT_ROADMAP.md), and [Issue #8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8). This is the single F00 research protocol; it specifies evidence collection without creating samples or running the study.

The research question remains whether systematic refactoring of AI-generated code reduces observed quality problems and technical debt while preserving tested behavior. All seven languages (Java, Python, JavaScript, TypeScript, C#, Go, C++) and real local Falcon-Mamba 7B remain mandatory first-delivery P0, along with deterministic security, dependency-aware patches, two product approvals, immutable originals/tests, isolated candidate and combined validation, ZIP, HTML/PDF and history. Java is the first pilot, not a reduced release scope. The >=12-task research dataset does not substitute for seven-language product acceptance.

| Evidence ID | Observed source / result | Classification and limit |
|---|---|---|
| E1 | Local root `C:\refactoring-ai-generated-code`; clean `main` tracking `origin/main`; fetch on 2026-11-02 left both at the baseline SHA | VERIFIED Git baseline. No prior local changes; task branch created without overwriting another branch. |
| E2 | `git log 7e068040c3a4fb1a2f32783a4c592dc974324f36`: ten 2026-09-27 commits from `2f9e72a` to `7e06804`; its tree has eight Markdown files | VERIFIED historical planning/scaffold. Original README defines Engineering Design II / Group B and quality/maintainability research; no executable pilot or measurements. |
| E3 | `git merge-base --is-ancestor` succeeds for historical `7e06804`, PR #38 merge `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c` and PR #39 merge `5c297836b9ec70112e7b662eac05ec966543a134` | VERIFIED ancestry; history retained. |
| E4 | Baseline has 53 tracked files: governance scripts/tests, approved requirements and planning; experiments, metrics and results contain README scaffolds | Governance IMPLEMENTED; actual checks in [handoff report](../../report.md). Application, pilot, adapters and research execution NOT_STARTED; no source/test freeze or measured outcomes. |
| E5 | Registry: active owner `cakarburkayy`, task `F00-PLAN`, no prerequisites, no confirmed handoff; Issue #8 open, zero comments when fetched on 2026-11-02 | VERIFIED task identity. Issue metadata is not academic approval or authority to advance rotation. |
| E6 | Latest [project status](../PROJECT_STATUS.md) records 34 tasks / 69 edges verified by Actions run 40518968864, attempt 2 | Recorded prior graph evidence, not a fresh full live-graph audit in F00. Registry and edges unchanged. |

Capability vocabulary: APPROVED_REQUIREMENT means authorized scope; IMPLEMENTED means an artifact exists; VERIFIED requires attributable execution/inspection evidence for the stated claim; NOT_STARTED means no implementation in the inspected tree; BLOCKED names an unmet gate; UNKNOWN means available evidence cannot establish the fact. Documentation alone never upgrades a product capability to VERIFIED.

Historical discrepancies are retained, not used as current policy: ADR 0001 and old task wording describe P1 local AI; the architecture diagram says optional Local AI; Issue #8 requests independent review; earlier ADR/status/workflow passages describe unapproved SRS, unmerged PRs or pending graph sync. Current SRS scope, [sole-owner decision](0004-sole-owner-approval.md), latest status and this task's explicit owner instructions supersede those statements. No architecture, SRS, registry, historical decision or native dependency is rewritten here.

## 2. Experimental unit, admission and freeze

One experimental task is a fixed AI-generated source baseline plus one bounded, evidence-supported quality refactoring objective in an identified component. It is not a GitHub issue, a provider retry or a complete language adapter. Distinct objectives sharing a source must declare shared provenance and dependency; they are not statistically independent samples merely because their IDs differ.

Register every candidate before evaluating refactoring results. Required fields:

- Stable task ID and dataset revision; language/component and fixed source scope.
- Source origin, source revision and permission/license reference; original generation prompt reference/hash, provider/model/revision/settings, UTC generation time and **all** generation attempt IDs/outcomes. If model revision is unavailable, state that limitation rather than inventing it.
- Immutable source artifact reference, per-file raw-byte SHA-256 manifest and manifest SHA-256; retained original archive hash when applicable.
- Selected quality finding IDs, tool/rule/version, severity, source/symbol location, raw scan evidence and bounded intended transformation.
- Baseline build/test commands and results, test-suite manifest/hash, coverage scope/result and applicable verification limits.
- Environment fingerprint: OS/architecture, hardware, runtime/compiler/build tools, dependencies/lockfiles, analyzer/rules/config hashes, isolation limits and relevant non-secret settings.
- Inclusion rationale, consent/access/retention references, known limitations and any relation to another candidate.

**Include** traceable authorized AI-generated source with a reproducible initial revision, a real supported quality finding, a bounded behavior-preserving objective, and executable relevant baseline verification in an approved isolated environment. Baseline tests must pass before admission to the main behavior-preservation cohort; test adequacy and coverage limits remain explicit. Preserve naturally generated defects/findings; do not plant smells or select only attempts likely to succeed. Dataset language/task composition and selection rationale are recorded before freeze; no invented language quota is imposed by this protocol.

**Exclude before freeze** only with a recorded reason: unknown provenance, missing permission, unresolved privacy/license conflict, corrupted input, incompatible objective (e.g. arbitrary security repair), or evidence that cannot support a reproducible baseline. A potentially remediable missing runtime/permission/evidence is BLOCKED pending a decision; it is not silently dropped. Broken-baseline/no-test negative fixtures belong to separately labelled product validation, not falsely passing research baselines. Record candidate counts and every exclusion/blockage so admission bias is visible.

| State | Meaning |
|---|---|
| EXCLUDED | Candidate fails documented admission rules before freeze; keep ID, reason and decision. |
| NOT_RUN | Eligible planned task/condition has not started; keep it in the planned-run ledger. |
| BLOCKED | A named prerequisite prevents execution/validation; record owner role and resolving action. |
| FAILED | Started attempt fails a required gate; retain all evidence and appropriate denominators. |

After freeze, a failed task is never retroactively EXCLUDED because its result is unfavorable. Withdrawals, consent changes or discovered invalid data require a visible protocol deviation and new dataset revision; retain counts and lawful non-sensitive audit metadata, and report the effect on comparability.

**Freeze procedure (later execution):**

1. Register at least twelve distinct eligible tasks and retain the complete screened-candidate ledger. Identify related samples and the fixed cohort; record evidence completeness and limitations.
2. Freeze exact task IDs, source revisions, original byte hashes, tests/test hashes, tool/ruleset versions, dependency and environment fingerprints, source/coverage scope, prompts/context configuration, provider/model/settings, retry/time/cost limits, condition/repetition schedule and analysis rules.
3. Verify hashes and run actual baseline builds/tests/scans in the approved environment. Attach logs, exit codes and raw reports; missing evidence prevents freeze.
4. Burkay records dated freeze approval of the dataset manifest hash and protocol revision, with the research evaluator's evidence review. Peer approval is optional. Only then mark the dataset FROZEN.
5. Corrections never overwrite frozen evidence. Create a linked revision with reason, approver, affected tasks and fresh hashes; rerun affected matched comparisons or report them NOT_COMPARABLE. Never mix results from different freezes without disclosure.

**Current availability:** zero registered experimental samples, zero frozen V0/test artifacts, zero executed research repetitions in the inspected repository. Dataset NOT_FROZEN. The minimum twelve tasks are a protocol requirement, not twelve fabricated records.

## 3. Java V0 and evidence preservation

F00-V0 (#9) must supply the real AI-generated Java 21/Maven pilot, prompt/model/attempt provenance, actual build and JUnit 5 regression evidence, and immutable V0/tests. JavaParser, PMD/CPD and JaCoCo evidence is introduced in the applicable analysis/test tasks; no tool installation or Java implementation is performed here. Generation failures and any pre-freeze repairs remain traceable; no planted smells, concealed attempts or test removal to obtain success.

Hash actual raw bytes with SHA-256, without newline/encoding normalization. A deterministic manifest uses sorted repository-relative paths and file SHA-256 values, explicitly recording its serialization/version; source and test manifests are separate. Hash the manifest bytes too. Preserve executable inputs, build descriptors, dependency locks and original archive separately from generated build output. Do not hash nonexistent files or treat a Git commit alone as byte-integrity evidence.

Refactor only working copies. Check original/test hashes after capture, before and after every candidate attempt, before final composition, and before export/reproduction. Hash mismatch blocks validation. Frozen tests/rules cannot be edited by a patch; additions or corrections require a traceable decision, a separate baseline revision and real revalidation. Passing one candidate does not replace final combined build, regression, quality and security checks on a fresh V0 copy. Build-only evidence leaves behavioral status UNVERIFIED.

Use existing artifact locations when actual artifacts are created; public repository storage is only for explicitly publishable material under [security policy](../../SECURITY.md). Restricted source/prompts/logs stay in owner-controlled storage with access controls, backup/integrity checks, approved retention duration and deletion procedure. Record retention/access decisions before intake; do not invent a fixed retention period. Preserve immutable evidence during authorized retention; a lawful deletion records non-sensitive reason/date and resulting reproducibility limits without retaining prohibited data.

Every evidence record has a stable evidence ID, artifact reference/hash, task/dataset/run/attempt IDs, actor, UTC timestamp, exact command or provider request metadata, input/output hashes, tool/model/config versions, start/end, exit/status and stderr/error references. Evidence links connect generation → V0/tests → findings → product approvals → patch attempts → individual validation → combined validation → final V1/export. Mask sensitive content before permitted egress/public reporting; keep redaction provenance without copying secrets. Do not send code externally or execute it on the host merely to collect evidence.

## 4. Measurement and fair comparison

### Quality and behavior

Compare the same frozen source/coverage scope, tool versions, rules/configuration, severity semantics and measurement units. Retain raw and normalized findings. Within each tool, deduplicate by declared stable identity (tool/rule/component/path/symbol or mapped location/evidence fingerprint); record moved, resolved, persisting and new findings. Correlate cross-tool overlaps explicitly, but do not sum unlike tool metrics or silently deduplicate unrelated findings.

For a declared comparable task/tool/rule scope let `B` be unique baseline findings and `A` be all unique post-refactoring findings in that scope, including newly introduced findings. `reduction_pct = 100 * (B - A) / B` when `B > 0`; when `B = 0`, display `N/A (zero baseline)`, including when new findings appear. Negative reductions are retained. Missing/failed scans or changed scope/configuration produce NOT_COMPARABLE, not zero findings. Record selected-target resolution separately from all-scope counts.

Keep `BEHAVIOR_STATUS = PASSED / FAILED / UNVERIFIED` separate from `QUALITY_OUTCOME = IMPROVED / UNCHANGED / WORSE / NOT_COMPARABLE`. For the declared comparable finding-count metric, `A < B` is IMPROVED, `A = B` UNCHANGED and `A > B` WORSE; retain severity/new-risk information separately. PASSED requires the frozen applicable tests and required build/type/coverage checks with real evidence, and is limited to that tested scope, not formal equivalence. Required test failures mean FAILED; missing/incomplete validation means UNVERIFIED. Required security, individual-validation and final-combination gates remain separate mandatory acceptance conditions. A finding reduction cannot qualify as success when behavior or those gates fail.

The **>=50% reduction is a target**, not an observed result. Predeclare per-task target success as comparable reduction >=50%, PASSED behavior and all applicable validation gates passed. Publish target-success count over all started task-condition executions, including failures; also show count over all planned executions. For descriptive cohort reduction use `100 * (sum(B) - sum(A)) / sum(B)` only over comparable measured pairs for one declared tool/scope, with pair count and missing/failed counts beside it. This descriptive subset is never the all-attempt success rate. Do not impute unmeasured after-values or aggregate unrelated analyzers/languages into a misleading single score.

Report complexity in the chosen tool's units and scope; duplication and coverage with exact numerator/denominator. Coverage change is percentage points when subtracting percentages. Retain new findings, uncovered code, incomplete scans and validation failures even if the targeted finding improves.

### Sequential versus parallel conditions (F15-EXPERIMENT #36)

Execute **three matched complete-dataset repetitions per condition**: `SEQ-R1..R3` and `PAR-R1..R3`, with task-level attempt IDs below each run. At twelve tasks this schedules 72 task-condition executions before any corrective attempts; none has run in F00. Sequential allows one job; parallel allows at most three genuinely independent jobs under the same frozen dependency/conflict rules. Unknown/shared side effects serialize; no artificial independence is asserted. Record observed concurrency and ineligible/conflicting tasks.

Each pair uses the same frozen tasks, V0/test hashes, selected findings, context content/hash and budget, tool/rule/environment settings, provider/model/revision and generation parameters, validation, retry and timeout budgets. Reinitialize isolated workspaces and reset run state. Record hardware/allocation, queue/load, network/provider variability and cache policy; hold these constant as far as possible, and disclose residual differences. Prespecify an alternating condition order (R1 SEQ then PAR, R2 PAR then SEQ, R3 SEQ then PAR), task order and seed where supported; do not tune settings after seeing results. The odd repeat count leaves a 2:1 order imbalance; disclose possible order effects. Provider nondeterminism is a limitation even with fixed seeds.

Measure monotonic wall time from enqueue of the fixed workload to terminal combined validation or run termination; record queue, provider, validation and human-approval wait separately. Use identical measurement boundaries and approval procedure in both conditions. Report whole-run elapsed time (not the sum of overlapping worker times), per-task durations, actual prompt/completion/cache token counts and actual billed cost/currency, accounting source and tariff date when applicable. Include retries and failed billable requests. Local execution records runtime/resource usage; token/cost fields are NOT_APPLICABLE when genuinely inapplicable, UNKNOWN when unavailable, and measured zero only with evidence. Never replace missing bills or usage with estimates.

For complete comparable pairs report `speedup_r = T_SEQ_r / T_PAR_r` for positive `T_PAR_r`, and `time_reduction_pct = 100 * (T_SEQ_r - T_PAR_r) / T_SEQ_r` for positive `T_SEQ_r`. Otherwise N/A. Failed/incomplete workload pairs do not establish throughput speedup; retain their measured elapsed time, completion counts and failure costs. Publish all three paired results, mean/median/range with valid-pair counts and limitations; three repeats do not establish a broad performance guarantee.

### Failure-inclusive ledger and denominators

Retain one row for every planned task-condition-repetition, and child rows for the initial candidate, each correction and each transport request. Maximum one initial candidate plus two corrections; transport retries have their own predeclared bounded budget. No invisible restart/retry; cancellation and resumed work link to the original record.

Record successful attempt, validation rejection, provider error, timeout, compilation failure, test failure, security rejection, conflict rejection, cancellation and environment blocker as explicit outcomes with stage/reason. A started operation that later blocks or is cancelled stays in started denominators. Pre-start blockers/NOT_RUN are separate from failed attempts but remain in planned totals. An EXCLUDED pre-freeze candidate is in screening totals, not the frozen cohort. Failed work is never removed to improve rates.

Publish `planned = not_started + started`; split not_started into NOT_RUN/BLOCKED/cancelled-before-start and started into terminal outcomes or still-incomplete. Report validated task successes / all started task executions, successes / all planned executions, and accepted candidates / all started candidate attempts, each with raw counts. Report failed transport requests / all issued requests separately so provider failures cannot disappear from reliability or cost. Count terminal outcomes once; retain multiple failure reasons as annotations. Zero denominator is N/A. Preserve measured partial time/tokens/cost and mark missing fields UNKNOWN with reason; no missing field becomes zero or an estimated success. If a run must be repeated, keep the failed run and identify the replacement and protocol deviation.

## 5. Resources, access and dependent work

Resource statuses: VERIFIED = directly checked for this claim; REPORTED = attributable statement only; UNKNOWN = not established; BLOCKED = unmet execution/acceptance gate; NOT_APPLICABLE = no requirement in the stated scope. Roles below describe accountability/contact, not a developer assignment or rotation change. On 2026-11-02 Burkay named “Alper Enes Ve Taha Uğur” as GPU/model and API/budget contacts; these correspond to roster members Alperen Enes Yaman and Taha Uğur Toyran. Per-resource allocation and actual access remain unverified.

| Resource | Required for | Current evidence | Status | Responsible role | Blocking dependent task / existing dependency | Next validation action |
|---|---|---|---|---|---|---|
| Local governance environment | F00 documentation checks | Windows checkout; Git 2.53.0.windows.3, Python 3.14.5; checks recorded in report | VERIFIED for this workstation only | Burkay, current task owner | F00-PLAN; no technical predecessors | Retain check results; other machines need their own verification. |
| Application development environment | Reproducible services/build/test | No application manifests/runtime in baseline; not installed/probed here | UNKNOWN | Later authorized environment task owner | F01-ENV (#10) depends on F01-GOV | Execute approved macOS/Windows clean-checkout validation in F01-ENV. |
| Java 21/Maven pilot tooling | Actual V0 generation/build/tests | No pilot or Java execution evidence; Java/Maven not inspected | UNKNOWN | Later authorized F00-V0 owner | F00-V0 (#9) depends on F00-PLAN | Verify versions and isolated build/test with recorded generation attempts. |
| Python, JS, TS toolchains | Language-specific source/build/test/coverage | Python interpreter exists for governance only; adapter/test/Node tooling not verified | UNKNOWN for adapter capability | Later authorized adapter task owners | F14-PY (#32), F14-JSTS (#33) depend on F13-BASIC + F04-JAVA | Validate real per-language fixtures/tools; Python availability alone is insufficient. |
| C#/.NET, Go, C++/Clang | Remaining mandatory adapters | SDK/compiler/compile-database availability not inspected | UNKNOWN | Later authorized adapter task owners | F14-CS/GO/CPP (#40–42), each depends on F02-CONTRACT + F06-SANDBOX + F11-VALIDATE | Record real parser/build/test/coverage and positive/negative patch evidence per task. |
| Secure isolated execution | Untrusted pilot/candidate/final validation | No implemented sandbox in baseline | BLOCKED for product execution | Later authorized sandbox/operator role | F06-SANDBOX (#16); existing registry prerequisites apply | Verify non-root, denied network/secrets and CPU/RAM/time/process limits with negative cases before executing untrusted code. |
| Falcon-Mamba 7B / compatible hardware | Mandatory real local security AI | Contacts reported by Burkay; exact device/access/model/runtime/memory/latency unverified | UNKNOWN; runtime gate BLOCKED | Reported contacts: Alperen Enes Yaman and Taha Uğur Toyran; Burkay coordinates | F07B-PILOT (#19) depends on F00-PLAN; F07B-LOCAL (#20) depends on PILOT + F07A-SCAN | Contacts confirm custodian/access; #19 measures exact model/runtime/device/quantization, memory and timeout. No VRAM/CUDA compatibility assumed. |
| Real patch provider/API permissions/budget | Authorized source egress and paid inference | Same reported contacts; provider/model, account authorization, quota and budget unknown | UNKNOWN; real provider execution BLOCKED | Reported contacts: Alperen Enes Yaman and Taha Uğur Toyran; Burkay approves policy/spend | F10-PATCH (#25) depends on F03-INPUT + F08-INTEGRATE + F09-SCHED | Confirm provider/custodian, consent, redaction, quota and spend limits without disclosing credentials; later authorized real validation. |
| Data/privacy/consent/retention | Pilot intake, research and external processing | No samples, permission records, retention decision or external-transfer consent | UNKNOWN; data intake BLOCKED | Source rights holder and Burkay/research evaluator | F00-V0, F03-INPUT, F15-EXPERIMENT; no new registry edges | Obtain traceable permission and distinct processing/egress/execution consents; approve storage/retention before collection. |
| Research dataset | >=12 frozen tasks and matched study | README scaffolds only; no registered tasks or hashes | BLOCKED / NOT_FROZEN | Later authorized research evaluator; Burkay freeze approval | F15-EXPERIMENT (#36) depends on F15-P0 + F00-PLAN | Select/register/freeze under sections 2–4 after actual pilot and required product evidence. |
| Academic/course scope | F00 acceptance | Burkay reports Hakan Çağlar verbally approved then-current GitHub scope on 2026-10-28; no documentary reference | REPORTED; owner accepts verbal evidence for AC-09 | Hakan Çağlar, reported academic approver; Burkay records acceptance | F00-PLAN acceptance; resolved under explicit owner instruction below | Preserve provenance/uncertainty; no further documentary gate imposed by this task. |
| Submission and capacity | Final delivery | Registry due 2027-01-01, exact time/channel unknown; 436–666 person-hours historical estimate | REPORTED date/estimate; UNKNOWN capacity/channel/time | Burkay/project coordination | F15-HANDIN (#37) depends on F15-P0 + F15-EXPERIMENT | Confirm channel/time and real available capacity; reforecast through approved planning process. No new deadline or scope reduction. |

These are resource impacts, not additional graph edges. F14-MIX already joins all five adapter tasks (covering seven languages); F15-P0 already requires F13-BASIC, F13-ADV, F07B-LOCAL and F14-MIX. Missing later resources do not require installing them during F00. Reported contacts do not authorize another active developer. Optional TÜBİTAK advisor/application eligibility is UNKNOWN and NOT_APPLICABLE to this authorized course-task acceptance unless separately pursued.

## 6. Separate academic approval record

On 2026-11-02 Burkay reported that **Hakan Çağlar gave verbal course-scope approval on 2026-10-28 for the then-current GitHub state**. Burkay subsequently confirmed no reference exists and explicitly directed that verbal approval be accepted and **AC-09 marked PASS**. This latest owner instruction supersedes the original request for independent documentary evidence for this criterion. It does not create a written academic attestation or GitHub approval comment.

Git inspection finds `67233482f2d10462933328c4b162d150bb4b0993` (2026-10-27 18:20:16 +03:00) as the latest reachable main commit before the end of 2026-10-28; fetched main remains there. This is a plausible repository scope reference containing approved SRS v0.4.0, **not proof of the precise branch/commit viewed by Hakan Çağlar**. Exact viewed revision and any independent approval artifact remain UNKNOWN/unavailable. AC-09 PASS means owner-accepted verbal evidence; external academic approval evidence remains REPORTED. Product-owner SRS approval, course approval and future SHA-bound PR approval are distinct.

## 7. Traceability and handoff limits

| Requirement | Protocol coverage | Later execution evidence |
|---|---|---|
| FR-009 | Sections 2–3: Java 21/Maven, real generation attempts, immutable V0/tests | F00-V0 (#9) |
| FR-047 | Sections 2, 4: >=12 fixed tasks, objective admission, failures in denominators | F15-EXPERIMENT (#36) |
| FR-048 | Section 4: three matched repetitions/condition, context/test/rule control, time/token/cost | F15-EXPERIMENT (#36) |
| FR-049 | Section 4: >=50% target, explicit formulas, missing/zero denominators, behavior separation | F15-EXPERIMENT (#36) |
| FR-050 | Sections 2–4: reproducible V0/V1, prompt/test/build evidence, limitations | F15-HANDIN (#37) |
| NFR-02 | Section 3: raw-byte SHA-256 and original/frozen-test integrity | #9, #13, #29 |
| NFR-04 | Sections 2–4: fingerprints, fixed scope and evidence identities | #15, #17, #30 |
| NFR-09 | One protocol, existing paths and governance; no infrastructure/framework | F00 scope/diff inspection |
| NFR-13 | Sections 1, 4–6: measured claims, resource uncertainty, attributed verbal approval | #19, #36 and actual resource checks |

Supporting safety traceability: FR-003–004, FR-030–036, FR-038–044 and NFR-01/03/05 cover original protection, consent, bounded concurrency/retries, separate results, validation and honest reporting. No requirement is claimed implemented by this protocol.

See [report.md](../../report.md) for actual acceptance/check outcomes and publication state. F00-V0 is a possible next candidate **only after** accepted F00-PLAN handoff; its implementation is not authorized here. Current owner remains Burkay, conditional next owner Cafer; no rotation advancement, milestone completion or release-readiness claim.

## 8. Mandatory report delivery — owner instruction, 2026-11-02

Burkay explicitly authorized committing/pushing this F00-PLAN work and required that **every authorized task** end with the actual report delivered in chat together with its verified Git SHA. Merely listing a local filename is insufficient. This instruction applies to subsequent task handoffs as part of the evidence-delivery protocol.

1. Update the existing `report.md` with task/owner, baseline, actual changes, acceptance, executed checks, limitations, publication state and conditional next owner. Preserve previous task reports through Git history.
2. When publication is authorized, review the exact contents, run applicable checks, commit/push the numbered task branch and verify that the remote SHA matches local HEAD. If publication is unauthorized or fails, report that with the current local SHA; never invent a published SHA.
3. The final chat response must include the full verified published SHA, commit URL, a **commit-pinned report.md URL** (or accessible Markdown attachment if GitHub is unavailable), real verification summary, PR/check status and remaining blockers. Include a readable task summary in chat. A local path alone does not satisfy report delivery.
4. A report cannot contain its own containing commit SHA. Keep BASE_COMMIT inside it; a later evidence-only update may reference a previously verified published task commit, explicitly labelled. Supply the final containing SHA and pinned report link in the chat receipt; do not generate endless self-reference commits.
5. Publication/chat delivery is distinct from merge, milestone completion and orchestrator acceptance. Stop at the authorized task boundary. This instruction authorizes the current task's publication; future tasks still require their own publication authorization.

This owner-directed rule uses the permitted decision/status/report paths. It does not bypass existing protected-path, CI, dependency or authenticated exact-HEAD approval checks. Protected skill and governance files remain unchanged.
