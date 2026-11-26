# ADR 0002 — Project Genesis v2.0 sequential ownership and mandatory first delivery

**Status:** PROPOSED MIGRATION / approved owner decisions, implementation review pending  
**Amended:** 2026-11-25 by [ADR 0007](0007-local-llm-and-approval-authority.md) — Falcon-Mamba 7B references below are historical; the local security model is now Qwen3-Coder 30B-A3B, and the single-final-approver rule is retired.  
**Date:** 2026-10-26  
**Decision authority:** project owner in project conversation.  
**Applies to:** `main` as accepted integration branch after independently reviewed and separately approved PR #38/bootstrap migration.

## Context

The older `chore/1-team-workflow` PR (#38) introduced a real five-member governance and prerequisite system. It contains **31 technical issues**, **six research work packages** and **54 native dependency edges**, with primary/support/reviewer fixed per task. Its trusted base is old `main`, so PR #38 itself requires manual current-revision independent review and owner authorization. These artifacts are valuable and must not be deleted or bypassed.

The later owner-approved Project Genesis v2.0 requires exactly one active developer, deterministic handoff and no permanent advance allocation of technical tasks. The owner also changed first-delivery priority: Falcon-Mamba and Python/JavaScript/TypeScript, mixed projects, PDF/HTML/history are mandatory P0, not deferrable P1. The SRS is to be delivered in Turkish and English and individually accepted later.

## Decision

1. Keep all 31 technical issues, their Plan IDs, six work packages, dependencies, original Git history, and meaningful per-task scope/test policy.
2. Remove fixed `owner`, `support` and `reviewer` fields from active task registry and epic records, while keeping the actual team's identity/membership.
3. Rotate **Burkay (@cakarburkayy) → Cafer (@caferkilinc) → Alperen Enes Yaman (@Yaman-A-E) → İsmail (@ismail-cevik) → Taha Uğur Toyran (@tahaugurtoyran) → repeat**; advance only once after verified human-reviewed publication, never when a prompt/test run/PR is merely created.
4. Record initial Burkay owner and first eligible `F00-PLAN` proposal as pending, not completed. PR #38 is **pre-Genesis**, does not consume a developer turn.
5. `main` is accepted integration branch. Keep numbered PR topic branches for independent reviewers, no uncontrolled concurrent active writers. Reviewer is independent from PR author and actual commit authors/committers, with relevant Write/Admin access and current HEAD approval. No single historical reviewer is permanently assigned.
6. Promote existing task issues **#19, #20, #31, #32, #33, #34** to mandatory P0. Java may be implemented first, but first delivery cannot be accepted without measured real Falcon-Mamba, Python, JS/TS and mixed-language capabilities plus full HTML/PDF/history.
7. Keep `docs/PROJECT_STATUS.md` and `docs/DEVELOPMENT_ROADMAP.md` instead of creating parallel equivalent files; `AGENTS.md` and project-local handoff skill contain only durable execution rules.
8. Existing PR #38 receives a **separate current-revision independent review and actual required checks**; the project owner must be asked for explicit approval immediately before merging. The same applies to any material governance migration PR. No direct change to `main`.

## Staged migration / stop conditions

- **Stage A (this proposal):** compile paired review-draft `docs/SRS.md` and `docs/SRS_EN.md`; update registry/closed-loop gate/tests/instructions in a **separate branch based on PR #38**, preserving the original PR. Do not claim the migration is active.
- **Stage B (review):** check changed governance code, run actual governance unit/CI/security/docs checks, and independently review the current migration revision. Resolve failures without weakening tests.
- **Stage C (bootstrap):** PR #38 must independently pass current checks, receive reviewer sign-off and explicit separate project-owner merge authorization. A PR merger cannot count the pre-Genesis work as a handoff.
- **Stage D (issue updates):** only after policy compatibility is accepted, migrate 31 live issue bodies/assignee lists and promote priority labels/metadata without erasing issues, history or native dependency edges. Repeat live-plan audit and verify graph equality.
- **Stage E (activation):** update canonical registry migration status with reviewed evidence, confirm first Burkay task/expected baseline and SRS acceptance, then begin sequential Codex implementation. Move rotation only after accepted handoff keyed by task+actual pushed commit.

If a required PR review, CI, permission, model hardware/runtime, API budget/consent or task prerequisite is missing, **stop the affected operation**. Never force-push, rewrite shared history, close/delete 31 technical issues or bypass governance to expedite the migration.

## Open blocking decisions and follow-up evidence

- Paired SRS v0.3.0 owner review/sign-off not yet recorded.
- PR #38 reviewer sign-off and **separate explicit final merge authorization** not yet granted.
- New migration branch CI/gate review and staged issue metadata updates not yet accepted.
- Falcon-Mamba 7B exact model/revision, quantization and compatible GPU/runtime not verified; a Mac M3 does not provide CUDA.
- Real cloud patch provider/model, privacy/consent, quota and potential spend not confirmed.
- First-delivery milestone schedule to 2027-01-01 requires capacity and critical-path reassessment; cannot guarantee feasibility from original estimates.

## Evidence identifiers

- Architecture: owner-supplied Master Architecture v2.0 / Step-by-Step Guide v2.0; current source summary in `docs/ARCHITECTURE.md`.
- SRS: `docs/SRS.md` and `docs/SRS_EN.md` (both review drafts).
- Git: PR #38, initial head `56cf49ce5472c9bfc2b3bbf29ad55f6eb3ffeb68`; no merge evidence at the time of this decision.
- Registry: `.github/task-plan.json` (31 technical tasks, 54 dependency edges).
- Governance: `scripts/governance/gate.py`, existing real test suites, `docs/TEAM_WORKFLOW.md`.

No product implementation, independent merge permission or production readiness is claimed by this ADR.
