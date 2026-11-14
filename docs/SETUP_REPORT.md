# GitHub ekip altyapısı teslim ve doğrulama raporu / Setup verification

> **23 October operational audit update:** [Operational audit and corrective actions](OPERATIONAL_AUDIT.md) supersedes earlier bootstrap descriptions of gate behavior/check coverage. 81 local governance/security regression tests pass; application checks remain future deliverables. A single explicit UI/environment prerequisite extends the live graph from 53 to 54 edges without adding tasks. The configuration remains unmerged pending Burkay’s independent approval.

Updated 23 Ekim 2026 / 23 October 2026; original audit 22 October. Repository: [caferkilinc/refactoring-ai-generated-code](https://github.com/caferkilinc/refactoring-ai-generated-code). [Project](https://github.com/users/caferkilinc/projects/1). [Configuration PR #38](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38).

Kurulum dosyaları inceleme branch’inde hazırlanmıştır; PR açık ve merge edilmemiştir. Yönetim altyapısı testleri çalışan bir ürün veya tamamlanmış araştırma deneyi anlamına gelmez. (Configuration is prepared on the review branch; the PR remains open and unmerged. Governance tests do not establish product or research success.)

## 1. Repository audit

`main` audit baseline: `7e068040c3a4fb1a2f32783a4c592dc974324f36`, ten September commits and eight Markdown files. Existing history is preserved. No executable application packages/tests or measured refactoring experiments exist in that base. Live repository visibility remains public and auto-merge is disabled. No direct main write, force push, history rewrite, paid service or private DOCX publication was performed. On 23 October the owner explicitly approved four Project Write grants, conditional merge after Burkay’s independent approval, and main protection after successful live validation.

| Operation | Status | Verified result / limitation |
|---|---|---|
| Repository access | COMPLETED AND VERIFIED | Cafer Admin; four collaborators Write, rechecked on 22 October |
| Six work-package trackers and 31 technical tasks | COMPLETED AND VERIFIED | All 37 issues fetched live; all open and assigned; no duplicate issue created |
| Task owner/support/reviewer/priority/date consistency | COMPLETED AND VERIFIED | All 31 live task bodies and assignees match `.github/task-plan.json`; six tracker assignees match |
| Native issue hierarchy and prerequisites | COMPLETED AND VERIFIED | Earlier hosted sync and API verification established 31 parent links / 53 edges; registry preserved in this pass |
| Five Project views and schedule | COMPLETED AND VERIFIED | Table, Board, Roadmap, Bug Tracking, Iteration / Sprint; saved shared defaults |
| Board acceptance automation | COMPLETED AND VERIFIED | Closure and merge → Testing; Auto-close issue is Off; Done requires reviewed acceptance |
| Private Project team access | COMPLETED AND VERIFIED | caferkilinc Admin; ismail-cevik, cakarburkayy, tahaugurtoyran and Yaman-A-E Write; all five listed after reload on 23 October |
| Governance tests and hosted CI | COMPLETED AND VERIFIED | 27 unit tests; documentation and hygiene checks pass; actual hosted evidence below |
| Configuration files | PREPARED | 36 changed files in PR #38; owner merge authorization received, independent review still pending |
| Independent PR approval | REQUIRES USER ACTION | Burkay requested; zero submitted reviews when checked |
| Trusted-main dependency gate | PREPARED | Read-only live preview passed; real base-triggered enforcement awaits bootstrap merge and canary checks |
| Main branch protection / rulesets | BLOCKED | Owner authorization received; independent review, bootstrap merge and successful live canary checks must precede activation |
| Application backend/frontend checks | NOT STARTED | Task #10 must supply real packages, lockfiles and commands first |
| Product implementation / scientific experiments | NOT STARTED | No implementation or numerical research success is claimed |

## 2. Project views, fields and automation

[Open Project](https://github.com/users/caferkilinc/projects/1). The same issue set feeds all views; trackers remain native parents rather than duplicated development work. Status order: Backlog → Ready → In Progress → Blocked → In Review → Testing → Done.

| View | Saved configuration |
|---|---|
| Task Table | `-label:type:epic`, 31 tasks; Assignee, Status, Linked PR, Estimated Effort, Start Date, Target Date, Labels |
| Development Board | `-label:type:epic`, same 31 tasks grouped by seven Status values |
| Roadmap | Start = Start Date; end = Target Date; technical-task filter; both fields verified selected after reload |
| Bug Tracking | `label:type:bug`; currently zero bugs, no fake issue created |
| Iteration / Sprint | `label:phase:F00,phase:F01,phase:F02`, six tasks for the initial 21 October–1 November planning block |

Estimated Effort is a Number; Start Date and Target Date are Date fields. All 31 task values were populated and checked earlier. Plan ID is in the title; owner is native Assignee; work package, phase, module and P0/P1 are labels; support/reviewer/contracts/acceptance are in the issue body; prerequisites are native issue dependencies. PR #38 is linked in issue #1’s body, without an automatic closing directive. No separate Reviewer/Plan ID/Dependency custom-field duplication or native recurring Iteration field is claimed.

Final verification corrected two inherited Done shortcuts: Item closed and Pull request merged now set Testing. Auto-close issue from Done is disabled. The built-in automations route work; they do not semantically verify acceptance. A maintainer must review the acceptance record and live evidence before setting Done. Six Project workflows remain enabled. Project description/README links the plan, workload, guide, PR and final deadline.

Project remains private. Following explicit owner approval on 23 October, `ismail-cevik`, `cakarburkayy`, `tahaugurtoyran`, and `Yaman-A-E` were each added with Project Write. Manage access was reloaded and showed all five accounts: caferkilinc Admin and four Write members, with no pending marker. Repository Write and Project Write are separate grants; both now cover the complete team. Visibility was not changed.

## 3. Research work packages

| Package | Owner | Tracker | Phases |
|---|---|---|---|
| İP1 — Deney temeli ve platform sözleşmeleri | @caferkilinc | [#2](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/2) | F00–F03 |
| İP2 — Dil çekirdeği ve başlangıç kalite/davranış ölçümü | @cakarburkayy | [#3](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/3) | F04–F06 |
| İP3 — Güvenlik inceleme hattı ve Local AI | @Yaman-A-E | [#4](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/4) | F07A/F07B |
| İP4 — İlk onay ve bağımlılığa duyarlı paralel refactoring | @Yaman-A-E | [#5](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/5) | F08–F10 |
| İP5 — Kanıta dayalı doğrulama ve nihai sürüm | @ismail-cevik | [#6](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/6) | F11–F13 |
| İP6 — Çok dilli genişleme ve deneysel değerlendirme | @tahaugurtoyran | [#7](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/7) | F14–F15 |

## 4. All technical tasks and dependency graph

The following is the exact mandatory integration graph. Independent topic-branch work may proceed with approved contracts/fixtures; dependencies gate integration. F07B / Local AI is P1 and never blocks Java P0. Contract Ready and Integration Ready tasks are distinct. Full technical deliverables, normal/error cases, allowed paths and applicable checks remain in the canonical registry and live issue bodies.

| Issue / Plan ID | Primary; support; independent reviewer | Priority | Start → target | Effort range | Prerequisites |
|---|---|---|---|---|---|
| [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 6–10 h | None |
| [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) `F00-V0` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) `F01-GOV` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-21 → 2026-10-25 | 8–12 h | None |
| [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) `F01-ENV` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) |
| [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT` | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 10–16 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) `F02-STATE` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) |
| [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 14–22 h | [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) |
| [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P0 | 2026-11-02 → 2026-11-08 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) `F05-QUALITY` | @cakarburkayy; @caferkilinc; @ismail-cevik | P0 | 2026-11-09 → 2026-11-15 | 16–24 h | [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) `F06-SANDBOX` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 18–26 h | [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17) `F06-TESTS` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-09 → 2026-11-15 | 12–18 h | [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14), [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) |
| [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) `F07A-SCAN` | @cakarburkayy; @ismail-cevik; @caferkilinc | P0 | 2026-11-16 → 2026-11-22 | 14–22 h | [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19) `F07B-PILOT` | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P1 | 2026-10-26 → 2026-11-01 | 6–10 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#20](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/20) `F07B-LOCAL` | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 14–20 h | [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21) `F08-UI` | @tahaugurtoyran; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-15 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) |
| [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22) `F08-INTEGRATE` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 8–12 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21), [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15), [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) `F09-CONTEXT` | @Yaman-A-E; @cakarburkayy; @caferkilinc | P0 | 2026-11-09 → 2026-11-15 | 18–26 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) `F09-SCHED` | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 10–16 h | [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) |
| [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25) `F10-PATCH` | @Yaman-A-E; @caferkilinc; @ismail-cevik | P0 | 2026-11-23 → 2026-11-29 | 18–26 h | [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13), [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22), [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) |
| [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) `F11-VALIDATE` | @ismail-cevik; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 18–26 h | [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17), [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27) `F11-RETRY` | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P0 | 2026-11-30 → 2026-12-06 | 6–10 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) |
| [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) `F12-REVIEW` | @tahaugurtoyran; @ismail-cevik; @cakarburkayy | P0 | 2026-11-16 → 2026-11-29 | 12–18 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21), [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) |
| [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29) `F12-FINAL` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-12-01 → 2026-12-06 | 14–22 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26), [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27), [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) |
| [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC` | @tahaugurtoyran; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 10–16 h | [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29), [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) |
| [#31](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/31) `F13-ADV` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 10–16 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) |
| [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32) `F14-PY` | @cakarburkayy; @ismail-cevik; @caferkilinc | P1 | 2026-12-07 → 2026-12-13 | 14–22 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) `F14-JSTS` | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P1 | 2026-12-14 → 2026-12-20 | 18–26 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#34](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/34) `F14-MIX` | @tahaugurtoyran; @cakarburkayy; @ismail-cevik | P1 | 2026-12-18 → 2026-12-20 | 6–10 h | [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32), [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) |
| [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35) `F15-P0` | @ismail-cevik; @tahaugurtoyran; @caferkilinc | P0 | 2026-12-07 → 2026-12-13 | 16–24 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) |
| [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) `F15-EXPERIMENT` | @caferkilinc; @Yaman-A-E; @ismail-cevik | P0 | 2026-12-14 → 2026-12-20 | 18–26 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35), [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#37](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/37) `F15-HANDIN` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-12-21 → 2026-12-27 | 10–16 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35), [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) |

Native sync evidence: [successful run](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39774558427). The previous API verification matched all 31 parents and 53 prerequisite edges. The graph has no cycle and no transitive Local AI blocker on a P0 task; these invariants also pass unit tests. No task has been closed to manufacture acceptance.

## 5. Team workload

| Account | Primary task count | Primary allocation | Support allocation | Combined estimate | Review assignments |
|---|---:|---:|---:|---:|---:|
| @caferkilinc | 8 | 83.3 h | 45.0 h | 128.3 h | 6 |
| @ismail-cevik | 5 | 65.8 h | 42.9 h | 108.7 h | 13 |
| @Yaman-A-E | 6 | 63.0 h | 19.2 h | 82.2 h | 0 |
| @tahaugurtoyran | 7 | 64.4 h | 6.0 h | 70.4 h | 0 |
| @cakarburkayy | 5 | 68.6 h | 34.8 h | 103.4 h | 12 |

Estimates distribute task midpoint effort 70% primary / 30% support over calendar days. They are planning assumptions, not measured working hours or equal weekly commitments. Reviewer/coordination time is additional, including interface feedback from Taha and Alperen. Epics add zero duplicated effort. See [weekly table](TEAM_WORKLOAD.md) and regenerate using `python3 scripts/governance/workload.py` after reviewed plan changes. Capacity peaks of approximately 19–26 estimated hours require weekly agreement; share work or defer independent/P1 work if unavailable. Critical dependent targets must move when prerequisite acceptance slips.

## 6. P0 / P1 roadmap and first sprint

| Date / window | Target |
|---|---|
| 21 October–1 November | Scope/evidence protocol, governance, API/CIR/LanguageAdapter contracts, pilot, reproducible environment |
| 2–15 November | Safe input/V0, Java adapter, real quality and sandbox/baseline, independent UI/context development |
| 16–29 November | Deterministic security, first approval integration, conflict scheduling, real provider patches |
| 30 November–13 December | Candidate/retry/combined validation, basic report, tested P0 E2E |
| 13 December 2026 | P0 acceptance target |
| 20 December 2026 | P1 cutoff; resource-permitting Local AI, extra languages and advanced reporting |
| 14–20 December | Frozen experiments, failure-inclusive analysis, explicit limitations |
| 27 December 2026 | Reproducible package and academic delivery preparation target |
| 28–31 December 2026 | Fix/regression reserve; no new planned features |
| 1 January 2027 | Final course delivery; no invented submission hour |

First actionable assignments: Cafer completes scope/resource decisions in #8 and presents #38 for review; Burkay reviews #38 and co-designs #11 adapter/CIR contracts; İsmail reviews scope/contracts and prepares #10 reproducibility/QA requirements; Alperen checks #19 GPU/runtime evidence and #25 provider access without paid calls; Taha checks approval/API consumption and prepares #21 mock fixtures. #11 integration follows accepted #8; #10 integration follows accepted #1. Do not mark mocks, a task description or a review request as completed implementation.

## 7. Branch protection and review

On 22 October the GitHub Branches page listed no classic protection and Rulesets explicitly said none exists. Therefore **GitHub is not currently enforcing the proposed merge restrictions**. The contribution guide is currently procedural. The [proposed protection JSON](../.github/branch-protection.proposed.json) specifies a PR, one code-owner approval, stale approval dismissal, successful current checks, resolved conversations, admin enforcement and no force-push/deletion. It is a proposal, not an active policy.

PR #38: primary @caferkilinc, support @ismail-cevik, independent reviewer @cakarburkayy. Zero submitted reviews were found. Neither author nor primary/support may supply independent acceptance. CODEOWNERS includes valid Write/Admin accounts and independent alternatives; it awaits merge to the default branch. The owner approved merge on 23 October, conditional on Burkay’s independent approval, and approved protection after live validation. Zero submitted reviews were returned when checked; this condition is not yet satisfied, so PR #38 remains unmerged. No second owner approval will be requested for the same unchanged scope.

## 8. GitHub Actions and actual validation

| Check / scenario | Result and scope |
|---|---|
| 27 governance unit tests | COMPLETED AND VERIFIED locally and in hosted Actions; isolated API fixtures |
| documentation-checks | COMPLETED AND VERIFIED; required documents and relative links |
| security-checks | COMPLETED AND VERIFIED; deterministic repository hygiene only, not a complete vulnerability scanner |
| Real bootstrap PR preview | COMPLETED AND VERIFIED in an earlier hosted push run: F01-GOV, zero mandatory prerequisites |
| Missing prerequisite / closed-only evidence | Unit rejection passes |
| Independent branch development / accepted dependency reevaluation | Unit positive cases pass; documented rerun procedure |
| Failed/missing CI and stale/self/primary/support review | Unit rejection passes |
| P0 independent of Local AI; branch/Plan ID/path traceability; cycle/API failure | Unit cases pass |
| Actual required-check merge blocking on main | PREPARED; not activated or live validated |
| Backend/frontend execution | NOT STARTED; no real app checks claimed before #10 |

Hosted evidence checked before the final documentation-only update:

- [CI run 39779470584](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39779470584) on `d5e3cce29cf7c14bc4de7d17e9bfda666af66b29`: governance-tests, documentation-checks, security-checks succeeded. Log confirms 27 tests. Preview is intentionally skipped for the PR event.
- [Earlier successful live preview](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39775623542): read-only GitHub API inspection of actual PR #38. This does not demonstrate trusted-main enforcement.
- Latest report-only commit triggers fresh CI; inspect its result on PR #38 rather than treating these earlier SHAs as evidence for a newer revision.

The privileged-event gate checks out only trusted base SHA and runs with read-only contents/issues/PR/check permissions; it never executes untrusted PR code. Ordinary governance CI has read-only contents permission. Owner-only graph synchronization has issues write, refuses unexpected reparenting/deletion and is not an arbitrary issue writer. Checkout is pinned to an immutable commit. A closed prerequisite alone cannot pass: trusted acceptance, merged matching PR/head, independent current Write approval, successful applicable checks and evidence are required.

## 9. Changed files and team guide

The initial bootstrap contained the following 32 changed paths. The audit adds `docs/OPERATIONAL_AUDIT.md`, `scripts/governance/audit_plan.py`, `tests/governance/test_audit_regressions.py`, and `.github/workflows/live-plan-audit.yml` (36 total):

```text
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/{bug,config,research,task}.yml
.github/PULL_REQUEST_TEMPLATE.md
.github/{acceptance,branch-protection.proposed,task-plan}.json
.github/workflows/{dependency-gate,governance-ci,issue-graph-sync}.yml
.gitignore
CONTRIBUTING.md
README.md
SECURITY.md
docs/ARCHITECTURE.md
docs/DECISIONS/0001-scope-and-governance.md
docs/DEPENDENCY_MANAGEMENT.md
docs/DEVELOPMENT_ROADMAP.md
docs/PROJECT_STATUS.md
docs/README.md
docs/SETUP_REPORT.md
docs/TEAM_WORKFLOW.md
docs/TEAM_WORKLOAD.md
scripts/governance/{check_docs,gate,github_api,security_check,sync_issues,workload}.py
tests/governance/test_gate.py
```

[Team workflow](TEAM_WORKFLOW.md) and [CONTRIBUTING](../CONTRIBUTING.md) explain issue → prerequisite check → updated main → numbered branch → code/tests → commit/push → PR → CI/review → approved merge → evidence acceptance → issue/board update. macOS M3 and Windows PowerShell examples are included. CUDA is never assumed on Apple Silicon. Product approval gates, GitHub review and research experiment counts remain distinct.

## 10. Remaining owner actions in dependency order

1. COMPLETED: owner authorization received and four Project Write grants verified on 23 October.
2. BLOCKED ON REVIEW: Burkay independently approves the final PR #38 revision. Owner merge authorization is already recorded; after the independent current-revision approval and successful CI, perform the authorized manual merge. No automatic merge is configured.
3. After approved bootstrap merge, run real canary checks on legitimate existing tasks. Verify trusted-base gate pass/fail, missing dependency/CI/review rejection and re-evaluation without faking accepted prerequisites.
4. After those live checks, activate main protection with only the five proven check names (including merge-readiness) under the owner authorization already received on 23 October. Proposed command from an authorized owner session: `gh api --method PUT repos/caferkilinc/refactoring-ai-generated-code/branches/main/protection --input .github/branch-protection.proposed.json`. It has not been executed.
5. Independently review trusted acceptance entries through a restricted governance PR. Re-run failed Dependency gate jobs or push a normal new commit after prerequisite acceptance; closing an issue alone does not reevaluate the gate.
6. Confirm weekly capacity, GPU/runtime and provider/data-transfer/budget decisions. #19 and #25 remain resource-blocked; no purchase or API consumption is authorized by this report.

Original user instruction preserves these approval boundaries: “PR’leri otomatik merge etme”, “Kullanıcı erişimlerini onayım olmadan değiştirme” and “Yalnızca ... kritik koruma ayarı ... veya merge gibi yüksek etkili işlemlerde açık onay iste.” The owner’s subsequent explicit approval on 23 October satisfies the access, conditional merge and conditional protection authorization requirements. It does not replace the independent reviewer or the live validation prerequisites.

## 11. Academic document continuity

The previously delivered five-person DOCX and role-swapped planning document remain preserved. They are academic/source documents, not automatically published files. The older H1–H12 schedule is superseded for implementation by the dated canonical GitHub plan; the GitHub instruction explicitly said not to rewrite the DOCX again. Taha retains Frontend/Reporting; Burkay retains Language Adapters/Analysis; Alperen retains Local AI/Parallel Refactoring. The public repository contains no academic DOCX. TÜBİTAK application/advisor eligibility and course approval remain separate decisions.

## 12. Completion boundary

Issues, assignment consistency, saved views, date/effort data, acceptance-safe routing and governance tests are established. Configuration files are prepared in the open PR. Private Project access is complete and verified. Owner authorization for conditional merge and protection is recorded. Burkay’s independent review, then merge and live main protection validation/activation remain sequential pending steps; the platform itself remains development work. (Görev sistemi ve test edilmiş kurulum hazırlanmıştır; erişim/onay/aktivasyon adımları açıkça beklemede tutulur.)

## 13. Owner authorization and execution update — 23 October 2026

The owner explicitly replied “onaylıyorum” to the concrete request for four Project Write grants, merge after Burkay’s independent approval, and main protection after live validation. Four Write members were added and verified after reload. PR #38 at `4e16940da6bb58a0dec92b47804a815570f72d59` had successful hosted CI ([run 39853424496](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39853424496)); the reviews API returned an empty list. Therefore no merge or main protection activation was attempted. This report-only update must also pass CI and be independently reviewed on its final revision. No extra owner approval is needed for the already authorized unchanged actions.


## 14. Operational audit correction — 23 October 2026

See [19 findings and their remedies](OPERATIONAL_AUDIT.md). Fixes include separate current-PR merge-readiness, fresh trusted-main reruns, current revision checks, author/committer independence, protected governance paths, complete changed-file scope, strict task graph/acceptance types, nested artefact/symlink hygiene, two-stage sync preflight, and read-only issue drift audit. All 81 tests pass locally; four workflow files parse correctly; documentation and hygiene checks pass. Live CI on the final revision is still the hosted authority, not the old 27-test SHA.

Existing task owners and dates stay unchanged. Required CI and scope notes were updated on #9/#10/#11/#21/#22/#30/#31/#34/#35. #21 now explicitly requires #10 for integration; contract/mock coding may still start in parallel. The canonical graph has 31 tasks, six work packages and 54 prerequisite edges. Estimated midpoint effort remains 493 hours excluding independent review; a separate review sensitivity table is now reproducible.

The audit does not activate untested protection, fabricate app checks, accept implementation tasks, merge its own PR, change team permissions, publish academic DOCX, or start paid services. Owner merge/protection authorization remains recorded; Burkay must approve the final reviewed revision before any merge.

Native graph update verified: [sync run 39870483114](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39870483114) succeeded, and #21 blocked_by was read as #11 and #10. No task was closed.

Hosted audit verification on code SHA `5af3b87469d02924c8f9a26a9593b6f119cb8de9`: [run 39870672707](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39870672707) passed all four jobs; logs confirm 81 tests and 31 live issue/graph consistency checks. [Graph sync 39870672750](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39870672750) also passed. The final document-only revision adds the verified historical academic-document drift finding (R19); inspect its latest PR CI separately.

## 15. F01-ENV local implementation — 8 November 2026

F01-ENV was implemented on `feature/10-f01-env` from canonical main revision
`9c50f649c2bcacfa700429b7ab7c97716b4d1475`, after the native dependency for
[Issue #10](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/10)
was verified as the completed [Issue #1](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/1).
The scaffold pins Python 3.13.17 and Node.js 24.22.2, commits `uv.lock` and
`package-lock.json`, provides FastAPI/Redis/SQLite readiness checks, and adds
backend, frontend, and application-stack workflows on GitHub-hosted runners.
The Compose stack does not mount the Docker socket or source directories and
uses read-only containers, non-root application images, and
`no-new-privileges` where supported.

Actual local results: `uv lock --check` passed; Ruff passed; seven backend tests
passed; one frontend test passed; and the Vite production build passed. Local
Docker/Compose execution is **NOT_RUN** because Docker is unavailable on this
host. Hosted CI is also **NOT_RUN** until publication. Consequently this is an
**IMPLEMENTED_LOCALLY / VERIFIED_LOCALLY / PENDING_PUBLICATION** record: no PR
has yet been accepted, Issue #10 remains open, and release readiness is not
claimed. The health scaffold does not execute uploaded code and is not a
substitute for the later isolated sandbox runtime.

### Local follow-up — 8 November 2026

Initial commit `38edd57af17f1a480f7f075c7eb1b85225ac8ad7` was published to the
feature branch. Its first PR creation attempt did not complete. The developer
then requested local development before authorizing hosted validation of the
follow-up changes.

Regression tests reproduced four failures in the initial scaffold: a
read-only SQLite database reported ready, an SQLite connection retained its
Windows file handle, and stalled Redis ping/cleanup operations lacked total
deadlines. The corrected probes pass all 13 backend tests. Storage probes roll
back their write transactions and explicitly close connections; Redis uses a
one-second operation deadline, a 0.2-second cleanup deadline and no retries.
The readiness endpoint probes the two dependencies concurrently. Docker build
inputs are restricted and the setup instructions now include explicit Windows
and macOS commands. Local Docker and native macOS execution remain NOT_RUN.

Follow-up verification: all 13 backend tests passed with Python resource
warnings treated as errors; Ruff lint and formatting, the unchanged dependency
lock, documentation and repository hygiene checks passed. All 55 contract
tests and deterministic export checks passed. Frozen V0 source and fixed-test
manifests still match their recorded hashes. The governance implementation was
not changed or re-tested in this follow-up; the earlier Windows symlink
privilege limitation still applies.
