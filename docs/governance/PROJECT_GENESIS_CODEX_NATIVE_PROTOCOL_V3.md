# Project Genesis v3.0 — GitHub development workflow

Developers work on a feature branch, open a pull request against canonical
main, run the applicable automated tests, and merge through GitHub after the
repository's required checks and reviews pass. Use normal GitHub authentication
and repository permissions. Issue links, acceptance criteria and evidence belong
in the PR. Use GitHub's native issue closure when the merged PR meets the criteria.

## Product tasks and checks

Use the trusted [task plan](../../.github/task-plan.json) for the current assignment,
task scope and technical prerequisites. Preserve GitHub issue dependencies and
[existing acceptance evidence](../../.github/acceptance.json). The read-only task
dependency audit reports scope and prerequisite discrepancies for registered
numbered branches. GitHub branch protection enforces the technical checks.
Include the actual checks required by the task, such as contract-checks for
F02-CONTRACT and schema changes. Keep immutable V0, frozen tests, security
controls and both end-user product approvals.

## Retired migration closure

[PR #49](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/49)
integrated the Genesis v3 implementation at
[2f9e05e0df886b250a690122b3369a45fee3fe96](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/commit/2f9e05e0df886b250a690122b3369a45fee3fe96).
The [migration reports](../reports/MIG-05.md) describe the implementation and
verification at that revision. The separate MIG-01 through MIG-05 acceptance
and lock procedure is retired. This decision creates no historical events and
consumes no product rotation turn.

This workflow supersedes repository execution and publication instructions in
the [v2.1 protocol](PROJECT_GENESIS_ORCHESTRATOR_PROTOCOL_V2_1.md), dated migration
reports, historical approval decisions and earlier repository governance clauses in the SRS. [ADR 0007](../DECISIONS/0007-local-llm-and-approval-authority.md) retires the single-final-approver rule of ADR 0004 and the delegation of ADR 0006; no owner approval marker is required. The approved [SRS TR](../SRS.md),
[SRS EN](../SRS_EN.md) and [architecture](../ARCHITECTURE.md) govern the product.
