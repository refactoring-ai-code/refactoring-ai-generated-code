# ADR 0007 — Local security LLM, cloud refactoring LLMs, parallelism and approval authority

**Decision date:** 2026-11-25
**Status:** ACCEPTED — recorded by the project owner, Cafer Tayyar Kılınç (@caferkilinc)
**Amends:** [ADR 0002](0002-project-genesis-v2-transition.md), [ADR 0003](0003-mandatory-seven-language-delivery.md), [ADR 0005](0005-f00-research-baseline.md), SRS v0.4.0 (TR/EN) → v0.4.1
**Supersedes:** [ADR 0004](0004-sole-owner-approval.md) (single final approver) and the delegation in [ADR 0006](0006-pr45-revision-bound-delegation.md)

## Context

The SRS made real local **Falcon-Mamba 7B** a mandatory P0 component for the
local security review. Falcon-Mamba 7B is a general-purpose model, not trained
for code. The task that should verify it (F07B-PILOT, #19) is still blocked:
no GPU access exists. In the meantime, a working prototype showed that the
security review works best when the LLM gets the deterministic AST/SAST findings
and a bounded context as input, and that patch generation needs a much larger
model than a local 7B one.

Governance documents also still described Burkay Çakar as the only required
final approver (ADR 0004) with the `GENESIS-OWNER-APPROVED: <SHA>` marker.
The v3 GitHub development workflow and the trusted gate no longer enforce that
rule, so the documents contradicted the actual process.

## Decision

1. **Local security model.** The mandatory P0 local security review model is
   **Qwen3-Coder 30B-A3B** (open weights, code-specialized, mixture-of-experts
   with about 3.3B active parameters per token). It replaces Falcon-Mamba 7B in
   every current requirement. Falcon-Mamba 7B may still be measured in F07B-PILOT
   as a comparison baseline, but it is no longer required.
2. **Local versus cloud.** Only the LLM that works together with the AST/SAST
   analysis (security review) runs locally. Refactoring/patch-generation LLMs
   run with authorized cloud providers (SRS provider adapters: DeepSeek, GLM,
   Qwen) on masked, bounded context packages. FR-016 (secret masking) and FR-032
   (egress, token and cost permission) apply unchanged.
3. **Unchanged rules for the local model.** Its findings stay UNCONFIRMED and
   evidence-linked (FR-055). Deterministic SAST continues when it fails. FR-054
   (pilot measurement) and FR-056 (precision/recall on independently labeled
   examples) now apply to Qwen3-Coder 30B-A3B.
4. **Hardware and budget (requested, not yet approved).**
   - Local: NVIDIA DGX Spark (GB10, 128 GB, 4 TB) or ASUS Ascent GX10 (same GB10
     chip and memory, 1 TB), available from local NVIDIA partners. Reported
     third-party throughput for this model on GB10: about 60–80 tokens/s.
   - Cloud API for refactoring: USD 100–200 total. The estimate is about
     3,200 calls (~20M input / ~13M output tokens), roughly USD 11–78 depending
     on the provider. A provider spending cap is mandatory.
   - Fallback if the budget is not approved: free Groq API keys (one per team
     member) for refactoring, and Qwen3-Coder 30B-A3B on a team PC with a 16 GB
     GPU served by llama.cpp.
   - ARM64 compatibility of the seven language toolchains and the model runtime
     must be verified on GB10 before purchase. F07B-PILOT records the measured
     model revision, quantization, memory and latency.
5. **Approval authority.** The single-final-approver rule of ADR 0004 and the
   `GENESIS-OWNER-APPROVED` / `GENESIS-DELEGATE-APPROVED` markers are retired.
   Pull requests follow the [v3 GitHub development workflow](../governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md):
   normal repository permissions, the required PR reviews and successful
   technical CI. The project owner records consequential scope, architecture,
   security-boundary and release decisions as ADRs. Historical approvals,
   including the 2026-10-27 SRS v0.4.0 approval, stay valid as records.
6. **Parallel refactoring jobs.** Up to **six** verified-independent refactoring
   jobs may run at the same time (FR-030; previously three). The conflict DAG
   rules stay: conflicting jobs and unknown symbol or side-effect relationships
   run one after another. Each job keeps its own isolated workspace and
   immutable input hash, so the validation sandbox must support six concurrent
   workspaces. Cloud provider rate limits can lower the effective parallelism;
   the free-tier fallback may run fewer jobs. Rough planning estimate (not
   measured): for 1 million lines (~500 fixes at ~1 minute each) refactoring
   drops from ~8.3 h with a single job to ~1.4 h with six.

## Unchanged

Seven-language P0 scope, immutable V0 and frozen tests, the two in-product
user approval gates, the 34-task / 69-edge dependency graph, the developer
rotation and all FR/NFR identifiers and priorities stay as they are. FR-048 still
compares sequential and parallel execution with three repetitions each.

## Consequences

- SRS TR/EN become v0.4.1. Model references in current requirements are
  updated; dated decision paragraphs and the original sign-off are kept and
  annotated, and the earlier wording remains in Git history.
- `.github/task-plan.json` records `Qwen3-Coder 30B-A3B` as the required local
  security model and `max_parallel=6` in the F09-SCHED acceptance criteria;
  issue text produced from the plan follows it.
- The two governance workflows that could only be triggered by `cakarburkayy`
  can also be triggered by the project owner.
- Release readiness still requires the real local model, measured on real
  hardware. A missing GPU remains a release blocker, not a reason to drop scope.
