# ADR 0003 — Mandatory seven-language first delivery and expanded dependency graph

**Decision date:** 2026-10-27  
**Authority:** Explicit project-owner instructions on 2026-10-27  
**Status:** APPROVED_SCOPE; implementation, native issue synchronization and release acceptance PENDING  
**Amended:** 2026-11-25 by [ADR 0007](0007-local-llm-and-approval-authority.md) — the mandatory local security model is now Qwen3-Coder 30B-A3B (replacing Falcon-Mamba 7B); refactoring LLMs run in the cloud.  
**Later state (recorded 2026-11-27):** the 34-task / 69-edge native graph, including the #40–#42 parent and prerequisite links, was verified by GitHub Actions run 40518968864 (attempt 2) on 2026-10-27; PR #38 was merged at `5754ed6` on 2026-10-27; both SRS texts were approved the same day. The pending statements below record the state at the decision date.<br>
**Supersedes:** Any 2026-10-26/historical interpretation that C#, Go or C++ adapters may be deferred beyond first delivery.

## Approved decision

The first delivery must provide **working, verified adapters for Java, Python, JavaScript, TypeScript, C#, Go and C++**, together with real local **Falcon-Mamba 7B**, immutable V0, two distinct user approvals, real authorized patch generation, candidate and combined sandbox validation, evidence-backed final ZIP and HTML/PDF/history. All are mandatory **P0**. Merely declaring adapters or showing disabled capability flags cannot count as release completion.

C# targets Roslyn and real .NET SDK build/test/coverage, Go targets module-aware parser/type/test/coverage, and C++ targets Clang/compilation database and real supported native build/test/coverage. Follow existing LanguageAdapter/CIR and sandbox interfaces; do not introduce an alternative execution architecture without owner approval. Toolchain/hardware/provider access must be measured; never invent successful build/latency/tests.

## Graph, identifiers and feasibility

Retain the **original 31 technical issues and all 54 original native predecessor edges**. Add unassigned P0 issues F14-CS [#40](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/40), F14-GO [#41](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/41), and F14-CPP [#42](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/42). Each requires F02-CONTRACT (#11), F06-SANDBOX (#16), F11-VALIDATE (#26).

F14-MIX (#34) now depends on F14-PY, F14-JSTS, F14-CS, F14-GO and F14-CPP. F15-P0 (#35) requires F13-BASIC, F13-ADV, F07B-LOCAL and F14-MIX. Downstream F15-EXPERIMENT and F15-HANDIN retain prior dependency constraints. Registry: **34 tasks, 69 total planned edges**; live native issue graph: **54 original edges plus the new links NOT YET VERIFIED/ACTIVATED**. Child links for #40–#42 to epic #7 are also pending. Safe synchronization and a complete live audit are required before dependency acceptance can be claimed. No old issue is deleted.

Historical schedule and resource estimates do not prove that this larger scope fits by **2027-01-01**. Produce an evidence-based critical-path reforecast after verifying .NET, Go, Clang and Falcon-Mamba resources.

## Team, PR #38 and review authority

The developer sequence remains Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran. PR #38 is **pre-Genesis**, consumes no rotation turn, and is not merged. The project owner designates **Burkay as primary technical lead and audit coordinator for PR #38**; this does not change the actual GitHub author (Cafer). An independent reviewer must not be the PR author or contributor to the reviewed revision. Burkay may perform technical coordination; if he contributed code, a separate independent reviewer must approve. **No merge without a later separate affirmative owner decision**, plus review and current-revision CI.

## Traceability and acceptance

See [Turkish SRS v0.4](../SRS.md), [English SRS v0.4](../SRS_EN.md): 62 P0 FR and 17 P0 NFR each (new FR-058–062, NFR-16–17). See [roadmap](../DEVELOPMENT_ROADMAP.md) and `.github/task-plan.json` for stable task IDs and dependencies. Both SRS texts remain final-approval drafts even though the scope decision is approved. Release remains NOT_READY until all mandatory behavior is verified.
