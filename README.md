# Secure Refactoring of AI-Generated Code

Engineering Design II — Ankara Bilim University. A planned multilingual platform for improving AI-generated code with controlled patches, reproducible analysis, isolated validation and two explicit product approvals.

**Current state (2026-11-27):** 9 of 34 tasks are accepted — F00-PLAN, F00-V0, F01-GOV, F01-ENV, F02-CONTRACT, F02-STATE, F03-INPUT, F08-UI and F04-JAVA: the Docker development environment (FastAPI backend, React frontend, Redis, SQLite), the CIR/API contracts, the workflow state machine and queue, authenticated source intake with immutable V0, the first approval UI (fixture data), and the language router with the Java symbol adapter (parse, symbol and dependency analysis through JavaParser). The active task is F05-QUALITY (#15, İsmail Çevik). Quality analysis, the other six language adapters, sandbox validation, security scanning, patch generation and reporting are not implemented yet; release remains NOT_READY. The 2026-11-25 decisions are recorded in [ADR 0007](docs/DECISIONS/0007-local-llm-and-approval-authority.md). See [actual status](docs/PROJECT_STATUS.md).

**Final course deadline: 2027-01-01; time unspecified.** All owner-approved Python/JS/TS, Qwen3-Coder, HTML/PDF and core refactoring capabilities are mandatory first-delivery P0; historical P1 schedule must be replanned. TÜBİTAK eligibility/application and advisors are separate, unverified decisions.

| Member | GitHub | Domain expertise (not fixed implementation assignment) |
|---|---|---|
| Cafer Tayyar Kılınç | @caferkilinc | Team Leader, FastAPI orchestrator, contracts, storage, integration |
| İsmail Çevik | @ismail-cevik | Sandbox, baseline tests, candidate/combined validation, QA |
| Alperen Enes Yaman | @Yaman-A-E | Local AI, context/conflict DAG, parallel refactoring, providers/retry |
| Burkay Çakar | @cakarburkayy | Language adapters, quality and deterministic security analysis |
| Taha Uğur Toyran | @tahaugurtoyran | Frontend, approval/diff screens, reporting/history, delivery demo |

The repository is `refactoring-ai-code/refactoring-ai-generated-code` (transferred from `caferkilinc`, same repository ID). On 2026-11-27 all five accounts had the Admin repository role.

## Scope

First-delivery P0: Java, Python, JavaScript, TypeScript, C#, Go and C++ (including mixed projects), real local Qwen3-Coder 30B-A3B, deterministic security, immutable V0, both user approvals, bounded real-provider refactoring, isolated candidate and combined verification, final ZIP, evidence-based HTML/PDF reports and history. C#/Go/C++ are also mandatory P0 first-delivery requirements per the owner decision on 2026-10-27, requiring real build/test/coverage/patch evidence. Lack of required GPU/provider access blocks release rather than becoming a fabricated PASS.

FastAPI/Redis/workers/storage and React/TypeScript/Monaco are planned components. No completed platform or measured improvement rate is claimed here. M3/macOS is a development environment; CUDA inference needs a separately verified GPU runtime.

## Working together

Start with [CONTRIBUTING](CONTRIBUTING.md), [team workflow](docs/TEAM_WORKFLOW.md) and the [GitHub development workflow](docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md). One authorized developer implements the registered task on a numbered topic branch. `main` is the integration branch. Private academic DOCX, raw user uploads and credentials stay outside this public repository.

- [Project board](https://github.com/users/caferkilinc/projects/1) (historical personal board from before the repository transfer; access not re-verified)
- [SRS Türkçe](docs/SRS.md) and [SRS English](docs/SRS_EN.md) (v0.4.0 approved 2026-10-27; v0.4.1 amendment by ADR 0007)
- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/DECISIONS/0001-scope-and-governance.md)
- [Roadmap and all 34 tasks](docs/DEVELOPMENT_ROADMAP.md)
- [Dependencies and gate](docs/DEPENDENCY_MANAGEMENT.md)
- [Weekly effort model](docs/TEAM_WORKLOAD.md)
- [Developer preflight and development workflow](docs/TEAM_WORKFLOW.md)

Governance verification (Python standard library, no dependencies):

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
```

These checks validate development infrastructure. They do not demonstrate product validation or research experiment success.


## Approved architecture and development state

The approved target is the v2.0 modular secure-refactoring pipeline, including immutable V0, per-language analysis, deterministic security + local Qwen3-Coder 30B-A3B, two user approval gates, bounded context/cloud LLM patching, individual and combined validation, all seven languages, and measured ZIP/HTML/PDF/history. Only the accepted tasks listed above are implemented; the remaining product capabilities are not yet proven. See [TR SRS](docs/SRS.md), [EN SRS](docs/SRS_EN.md), [architecture](docs/ARCHITECTURE.md), and [roadmap](docs/DEVELOPMENT_ROADMAP.md).

Implementation ownership rotates one at a time: **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat**, after evidence-based handoff acceptance. The current owner and task are recorded in `.github/task-plan.json`. `main` is the integration branch; pull requests follow the GitHub development workflow (repository permissions, required reviews and successful CI). Model hardware and cloud provider budget are requested but not yet verified.

The task graph has 34 tasks and 69 dependency edges (the 31 original issues and 54 original edges are preserved), verified on GitHub on 2026-10-27.

### Decision history
PR #38 (pre-Genesis governance bootstrap) was merged on 2026-10-27 and consumed no rotation turn. The former single-final-approver rule ([ADR 0004](docs/DECISIONS/0004-sole-owner-approval.md)) was retired by [ADR 0007](docs/DECISIONS/0007-local-llm-and-approval-authority.md) on 2026-11-25.
