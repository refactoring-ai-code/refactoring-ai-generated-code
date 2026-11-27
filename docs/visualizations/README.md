# Interactive SRS UML Studio

**Source of truth:** [Turkish SRS v0.4.1](../SRS.md), [English SRS](../SRS_EN.md), [Architecture](../ARCHITECTURE.md), and project-owner decisions in [AGENTS.md](../../AGENTS.md).

Open **[uml-studio.html](uml-studio.html)** as a saved local HTML file (or from raw GitHub content) in a modern browser. It uses inline SVG, no network assets, and offers **two views only** — Use Case and Class Diagram. Use drag-to-pan, scroll-to-zoom, *Fit*, fullscreen, search, and click-to-inspect SRS requirement references.

## Use Case view (UC-01–UC-19)

| Group | IDs | Responsibility |
|---|---|---|
| Input/permissions | UC-01, UC-02 | Secure ZIP/folder/snippet, V0, consent |
| Analysis/test | UC-03–UC-06, UC-19 | Adapter routing, AST/static quality, deterministic security, sandbox frozen tests, local AI auxiliary review |
| Human gate 1 | UC-07, UC-08 | Evidence inspection, eligible QUALITY_REFACTOR selection |
| Patch/validation | UC-09–UC-12 | Dependency context, bounded real diff, candidate validation, Monaco-style diff review |
| Human gate 2 | UC-13 | Explicit and separate patch approval |
| Combined final/results | UC-14–UC-18 | Fresh V0, full regression/security scan, before/after metrics, artifacts, History |

**Stereotypes:** `«include»` means the calling use case reuses required behavior; `«extend»` denotes conditional auxiliary behavior (the local Qwen3-Coder review is advisory, never a security verdict). **Security findings are not automatically eligible quality refactoring targets.**

## Class view (24 conceptual elements)

- Versioned source/permissions: `Project`, `ProjectVersion`, `ConsentRecord`, `FileManifest`, `Artifact`, `AuditEvent`.
- Evidence & tests: `AnalysisRun`, `Finding`, `Evidence`, `Metric`, `BaselineTestSuite`, `TestRun`.
- Refactoring: `IssueSelection`, `ContextPackage`, `RefactorJob`, `Attempt`, `PatchCandidate`, `ValidationResult`.
- Release and language contract: `PatchApproval`, `CombinedValidation`, `Report`, `LanguageAdapter`, **7 adapter package** (Java, Python, JavaScript, TypeScript, C#, Go, C++), `CapabilityReport`.

This is a **conceptual class model**; the SRS does not dictate physical ORM schema. The `«package» 7 Adapters` view groups the seven mandatory language-specific implementations; it is not a claim that one production class replaces seven adapters.

## Delivery boundary

This is presentation/documentation only: product backend/frontend, real seven-language E2E, Qwen3-Coder and consolidated validation must be established through code and tests independently. This documentation commit must not be misclassified as IMPLEMENTED/VERIFIED. Neither original V0 nor frozen suites are rewritten by the diagram work.

**Superseded files removed from PR #43 branch:** `architecture-atlas.html`, and the initial `use-case.puml` / `class-diagram.puml` sketches. Historical Git commits remain immutable; these files are absent from the new branch HEAD.
