# GitHub issue dependencies and technical checks

The [GitHub workflow](governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) uses
native issue prerequisites and real test results. The task registry maps issues
to scope, acceptance criteria and required technical checks.

The read-only dependency audit runs trusted main code for PRs targeting main.
It uses the issue number in registered topic branches, checks the complete file
scope and compares the GitHub prerequisite set with the registry. Existing
acceptance records retain their merged PR, revision and CI evidence. For tasks
completed under the current workflow, review the merged PR and its evidence
before marking the issue completed in GitHub. The audit reports prerequisite and
scope findings separately from required branch protection.

## Real checks for each deliverable

| Task / scope | Required application evidence | Who supplies the real workflow |
|---|---|---|
| #9 Java pilot | `pilot-checks`, real Maven/JUnit pilot build/tests | #9 may add `.github/workflows/pilot-checks.yml`; no Python environment dependency is invented |
| #11 CIR/API contracts | `contract-checks`, actual schema/fixture validation | #11 may add `.github/workflows/contract-checks.yml` so early contracts need not wait for #10 |
| #10 environment | backend-checks and frontend-checks | #10 supplies real pinned packages, lockfiles, test commands and application CI |
| #14 Java language adapter | backend-checks builds the JavaParser helper (JDK 21, checksum-verified Maven 3.9.11) and runs `tests/language_adapters` with the Monaco cross-check | F01-GOV adds the workflow steps; #14 supplies the adapter, helper and tests within its allowed paths |
| #22, #30, #31, #34, #35 mixed delivery / E2E | backend-checks and frontend-checks | Actual app checks from #10; mixed/E2E task evidence is also reviewed |
| Any PR changing backend or frontend | Adds corresponding check based on actual changed paths | A frontend task label cannot hide backend code |
| Schema paths / contract tests | Adds contract-checks | Real contract tests; no fake green command |

Verify each required workflow's existence, runtime and result on the relevant revision before granting readiness or acceptance. The #21 → #10 integration edge records the UI's environment prerequisite.

## Synchronization and drift

Issue graph sync performs a complete read preflight before the first write; unexpected parents/edges stop the run. It only adds expected missing links. GitHub writes are not a transaction: an API/network failure during the write stage can still leave a partial result. Re-run the idempotent sync after fixing the cause, then audit; do not erase history or delete unrelated edges.

`python3 scripts/governance/audit_plan.py` audits all registered task metadata bodies, six parent lists and native prerequisites with read-only API requests. After merge, the owner may run Actions → Live plan audit on main. This is a diagnostic, not a required merge check: dispatch-only workflow jobs are not eligible required PR checks. Personal Project date/effort cells still need a separate board comparison; `GITHUB_TOKEN` access to a repository does not grant access to a private personal Project.
