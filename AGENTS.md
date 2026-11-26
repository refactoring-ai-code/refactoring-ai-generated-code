# Repository Codex instructions — Project Genesis

> **Execution policy:** Follow the [GitHub development workflow](docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md). Verify canonical main and the current task before changing product code.

Project: secure refactoring of AI-generated code (**Java, Python, JavaScript, TypeScript, C#, Go, C++ and a local Qwen3-Coder 30B-A3B security LLM**, all P0 first-delivery); preserve owner-approved Master Architecture v2.0 and Step-by-Step Development Guide v2.0.

## Source hierarchy
1. Explicit owner decisions (2026-10-26, 2026-10-27 and 2026-11-25 / [ADR 0007](docs/DECISIONS/0007-local-llm-and-approval-authority.md): local security LLM Qwen3-Coder 30B-A3B, cloud refactoring LLMs, no single final approver): `main` is accepted integration branch, PR #38 was explicitly owner-authorized and merged (2026-10-27), all #19/#20/#31/#32/#33/#34/#40/#41/#42 are first-delivery P0; verified seven-language acceptance is mandatory.
2. SRS: `docs/SRS.md` and `docs/SRS_EN.md` (v0.4.0 approved 2026-10-27; v0.4.1 amendment recorded by ADR 0007 on 2026-11-25); conflicts require owner decision.
3. Architecture: `docs/ARCHITECTURE.md` plus owner-provided v2.0 primary source PDFs (not assumed present in public repository).
4. Planning and actual state: `.github/task-plan.json`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/DECISIONS/`, `.github/acceptance.json`; actual repository and tests establish IMPLEMENTED versus VERIFIED.
5. See approved scope record `docs/DECISIONS/0003-mandatory-seven-language-delivery.md`; see `docs/TEAM_WORKFLOW.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/DEPENDENCY_MANAGEMENT.md` for applicable detailed practice.

## Stable execution invariants
- The task registry identifies the current product task and developer. The product rotation is **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → Burkay**. Governance maintenance consumes no turn. Verify native dependencies and preserve historical acceptance records.
- Do not modify source unless a bounded authorized task specifies its owner, ID, scope, dependencies, approved baseline, acceptance, verification and stop conditions. No next-task implementation after reporting.
- Before edits: identify root, clean/dirty worktree, HEAD, branch, remote/upstream and last accepted commit; stop on unsafe divergence or unexpected changes. Do not force push, reset --hard, clean, discard existing work or assume a PR is already merged.
- No unapproved architecture changes, extra infrastructure, speculative dependencies, unrelated refactors, test inflation, credentials, production secrets or unattended deployment.
- Honor immutable V0 and frozen test hashes. A successful build is not proof of behavioral preservation. Validate candidates individually and final combination, retaining separate behavioral and quality results. Do not weaken tests or leak secrets to models, logs or reports.
- Use actual repository-supported commands, record PASS/FAIL/NOT_RUN honestly; after two unproductive repair guesses without new evidence, stop and escalate.
- Record the actual verification results and merge evidence in the PR. Use the GitHub workflow and applicable technical checks.
- For authorized implementation or repair use `.agents/skills/development-handoff/SKILL.md` when installed/supported; otherwise follow an equivalent concise contract. Load only task-relevant context.

## Publication authority

Use normal GitHub permissions, applicable PR reviews and successful technical CI. Preserve task scope, acceptance criteria and native issue dependencies. PR #38 and ADR 0006 document historical decisions.

## First-delivery language acceptance
All seven language adapters require real symbol/quality/build/test/coverage and bounded validated patch evidence where applicable. F14-MIX depends on #32/#33/#40/#41/#42; F15-P0 also requires real local security AI and full PDF reporting. The 34-task/69-edge GitHub-native issue graph is VERIFIED (Actions run 40518968864, attempt 2); 31 original tasks and 54 original edges are preserved. Dependencies are prerequisites, not completion evidence. Do not state release READY if a mandatory language, model, negative-path, or combined-test gate is unverified.
