# F05-QUALITY handoff

[F05-QUALITY / #15](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/15)
is owned by İsmail Çevik (@ismail-cevik). The verified starting revision is
`10748975ac0b81550d5ab23d6ea39f90db476d89`. The prerequisite F04-JAVA
acceptance records [PR #67](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/67)
at merge `2c3d35a70b2c94e12fe172392a6098dc0ab520d5`.

## Delivery

The storage-backed Java analyzer runs pinned PMD and CPD 7.29.0 on the
manifest-selected files of verified V0 copies. It emits CIR 1.0.0 findings,
locations, evidence, capability and metric records. Raw XML is retained by
SHA-256. A CPD API renderer uses manifest-relative paths because the pinned
CLI XML renders absolute paths. The artifact references preserve each tool's
independent evidence. See the [F05 technical guide](docs/F05-QUALITY.md)
for installation, metric definitions and evidence storage.

## Acceptance

| Criterion | Local evidence |
|---|---|
| AC1 Four source-located quality categories | Real PMD Design, Best Practices, Error Prone and Code Style findings with resolved source ranges. Real CPD matches retain all occurrences. The frozen Java pilot was analyzed through the snapshot store. |
| AC2 Tool, rule, scope and unit | Tests check actual tool versions, configuration and XML digests, rule identifiers, source references, comparison scope, environment and COUNT units. Generated bundles pass CIR graph validation. |
| AC3 Distinct duplication metrics | Real CPD token and line counts have separate names and comparison keys. |
| AC4 Comparable measurements and Sonar independence | A real change of scanned paths changes comparability. Controlled changes to tool and rule provenance also produce NOT_COMPARABLE. The real suite runs without SonarQube. |

## Verification

Windows native PowerShell, CPython 3.13.17, uv 0.13.7, Temurin 21.0.11 and
checksum-verified Maven 3.9.11 and PMD/CPD 7.29.0 were used.

| Check | Result | Observed evidence |
|---|---|---|
| Ruff on analyzers, language adapters and their tests | PASS | Locked backend environment, all checks passed |
| Maven JavaParser helper build | PASS | Pinned Maven package command exited 0 |
| Language adapter and quality pytest suite | PASS | 38 passed, including 11 F05 cases, 0 skipped |
| Backend pytest suite | FAIL | 38 passed, 1 failed on Windows. The existing ZIP path case `test_unsafe_paths_are_rejected_without_persistence[paths2]` accepts `dir\file.txt`, a known baseline failure |
| CIR/API contract checks | PASS | 55 passed, including graph semantics and generated exports |
| CIR export check | PASS | Generated exports are current |
| Governance Python tests | FAIL | 83 executed, 2 existing symlink tests raised WinError 1314 |
| Local documentation links | PASS | Required project artifacts and links verified |
| Local repository hygiene | PASS | Repository hygiene command exited 0 |
| Frozen pilot before and after quality execution | PASS | All 5 V0 files and the fixed test matched their manifests |
| Git diff whitespace and protected paths | PASS | No whitespace errors or changes in protected paths |
| Hosted GitHub PR checks and independent review | NOT_RUN | No PR head or review was requested during this delivery |

The two governance errors are `test_directory_link_not_followed` and
`test_file_link_not_followed`. These and the ZIP path baseline failure
were previously recorded in the [project status](docs/PROJECT_STATUS.md).
Under the verification policy they prevent claiming full LOCAL_VERIFIED.

The existing `backend-checks` job discovers the F05 pytest directory
under `tests/language_adapters`, but its environment does not install
PMD/CPD and its lint target excludes `backend/analyzers`. Hosted
verification is blocked until the separate governance CI work addresses these
gaps. A missing distribution fails the real acceptance tests explicitly. The
feature change keeps workflows and the acceptance registry out of scope.

## Continuity

The feature branch is `feature/15-f05-quality`. Integration and the separate
acceptance record are pending. The dependency audit rejected the README status update under F05 scope, so the README update is deferred to the separate governance acceptance record. İsmail Çevik retains task ownership. Taha Uğur
Toyran (@tahaugurtoyran) is the next conditional owner after acceptance.
