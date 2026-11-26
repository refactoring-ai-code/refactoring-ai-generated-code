# ADR 0006 — Revision-bound delegated approval for PR #45

Date: 2026-11-04 (Europe/Istanbul).<br>
State: PREPARED_FOR_REVIEW; activation on trusted main is pending.<br>
Status update 2026-11-25: historical; superseded by [ADR 0007](0007-local-llm-and-approval-authority.md) (no owner or delegated approval marker is required any more).<br>
Task: F01-GOV / #1, bounded approval-policy maintenance authorized in this chat.<br>
Developer: Cafer (`caferkilinc`).<br>
Approved preparation baseline: `aa7d2c810a3c19dbc92bd6efa69c517a598dde7e`.

## Authority and provenance

Cafer supplied Burkay's messages dated 2026-11-03 at 21:22 local time, reporting
that Burkay reviewed the work, found no defect and wanted the developers to
record approval themselves. This is **REPORTED off-platform delegation**, not
an authenticated GitHub approval from `cakarburkayy`. No owner comment or
provider identity is fabricated. On 2026-11-04 Cafer explicitly requested that
the delegation and necessary governance change be handled in this chat.

That user instruction authorizes preparing this narrow policy maintenance and
its tests despite the older F00-V0 protected-file restriction. It does not
authorize an automatic merge of PR #45, issue closure, acceptance-registry
mutation, rotation advancement, broad future delegation or unrelated work.
The active registry remains Cafer / F00-V0, rotation index 1. This maintenance
preparation is not a new implementation rotation turn. All recorded source
requirements and the seven-language P0 scope are unaffected.

## Proposed decision

Preserve the ordinary Burkay exact-HEAD approval path from ADR 0004. Add one
explicit exception to its final-approver rule, with **every** boundary required:

| Boundary | Exact value |
|---|---|
| Repository in trusted plan and PR base/head | `caferkilinc/refactoring-ai-generated-code` |
| PR | `45` |
| Task and issue | `F00-V0` / `9` |
| Target branch | `main` |
| Source branch | `feature/9-java-v0-pilot` |
| Source author and delegated comment author | `caferkilinc` |
| Authorized source HEAD | `d923134da4f9f5a2ab55a5f51fbf9415ff717262` |
| Exact delegated comment body | `GENESIS-DELEGATE-APPROVED: d923134da4f9f5a2ab55a5f51fbf9415ff717262` |

Cafer's delegated marker records Cafer's own authenticated GitHub action. It is
different from `GENESIS-OWNER-APPROVED`; Cafer cannot use that owner marker to
impersonate Burkay. Changing any listed boundary invalidates the exception.
There is no wildcard, SHA prefix match, automatic approval, PR-body override,
environment-variable override or general self-approval permission.

All task-ownership, complete-path, prerequisite, native-dependency, CI-origin,
successful-required-check and trusted-main/head freshness checks continue to
apply. Missing/failed/skipped required checks still block readiness. The grant
stays as revision-bound historical evidence for downstream prerequisite
verification after a separately authorized merge/acceptance; it never applies
to a new commit or another PR.

## Scope and acceptance of this maintenance

Allowed files: `scripts/governance/gate.py`,
`tests/governance/test_pr45_delegation.py`, this ADR, the dependency-policy note
and `docs/reports/pr45-approval-delegation.md`. Root `report.md` stays unchanged
to avoid a conflict that would invalidate PR #45's SHA. No workflow, registry,
acceptance record, SRS, roadmap,
application source, V0, test fixture or pilot manifest changes.

Acceptance requires a valid delegated-readiness case; rejection of missing or
stale/wrong-author approval, owner-marker impersonation, different PR/SHA/task/
branch/repository/author, missing prerequisite and missing/failed/skipped CI;
continued ordinary owner approval and historical prerequisite verification;
the full governance suite, documentation, limited security hygiene and complete
whitespace/scope review. Record actual outcomes in the maintenance report.

## Activation boundary

The dependency workflow executes **current trusted main**, not PR head code.
Until this policy is integrated into main, the existing readiness run will
continue to reject Cafer's comment. Publishing this proposal or posting a
delegated comment does not activate it. The current main also identifies
F00-V0 as the single active task, so a separate #1 proposal cannot pass its
existing dependency gate merely by changing its own branch policy.

Prepare and test first; present the exact reviewed commit/diff and outstanding
bootstrap limitations. Integration of this governance change needs an explicit
decision in this chat. No check conclusion is manually set to success and no
required check is removed. After authorized activation, Cafer can record the
delegated marker and the dependency/readiness workflow can be rerun against
the new trusted main. PR #45 merge and handoff acceptance remain separate
decisions and are not performed by this maintenance preparation.
