---
name: verification
description: Select and run evidence-based checks for an authorized Project Genesis change. Use for local test results, protected-file integrity and final Git diff review.
---

# Project Genesis verification

## Select and run actual checks

Use the authorized contract, pinned task entry and actual changed paths to determine mandatory checks. Map them to real commands in existing build manifests, test directories, repository instructions or GitHub Actions workflows. Cover applicable build, unit, integration, contract, governance, documentation, security, static analysis and regression checks. Start with focused checks and run all mandatory broader checks. When a required command or prerequisite is unavailable, record the reason instead of substituting a weaker check.

Existing governance commands are defined in [Governance CI](../../../.github/workflows/governance-ci.yml). Use the available Python launcher for the current shell and OS.

```text
python -B -m unittest discover -s tests/governance -v
python -B scripts/governance/check_docs.py
python -B scripts/governance/security_check.py
```

Capture the check ID, actual command, environment, exit code if executed, result summary, evidence location, source revision and limitations. A passing build establishes build evidence. Behavior or security claims require their own checks.

| Result | Evidence |
|---|---|
| `PASS` | The intended check ran and met its success criteria. |
| `FAIL` | The check ran and produced a failure or a contradictory result. |
| `NOT_RUN` | No execution occurred. Skipped checks are recorded here with the reason. |
| `BLOCKED` | A known dependency, unavailable test or unsafe condition prevents required verification. |
| `NOT_APPLICABLE` | The check does not apply to the verified scope. Record why. |

A required check in any state other than `PASS` prevents `LOCAL_VERIFIED`. `HOSTED_VERIFIED` requires independent GitHub evidence for the applicable revision and checks. `HANDOFF_ACCEPTED` requires the separate acceptance process under the effective policy.

## Inspect Git scope and protected bytes

Compare the final branch, `HEAD`, staged and unstaged diffs, untracked paths and relevant ignored outputs with the [bootstrap](../repo-bootstrap/SKILL.md) inventory. Include new files and both sides of renames. Check allowed paths, unrelated files, generated output, credentials and protected changes. Separate starting changes from work introduced by the task. Use `git diff --check` for tracked diffs and inspect untracked additions separately.

Compare protected files against the approved starting Git blobs and check the approved manifests where required. Use `git hash-object --no-filters -- path` or a raw SHA-256 digest to detect byte differences. Treat unexpected protected changes as failures and stop without modifying the protected file.

The former `v0-source.json` frozen-pilot manifest mismatch was resolved by [PR #48](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/48) (merged 2026-11-04); `experiments/java-pilot/verify_integrity.py` passes on current `main`. If the integrity command fails, report it as `FAIL`. Checks that depend on the affected frozen input remain `BLOCKED`. Independent checks may still pass. Compare against the starting bytes to distinguish a pre-existing discrepancy from a task change. Keep the frozen pilot and manifests intact.

For failures, make only a justified, bounded repair within task scope. Stop after two speculative attempts without new diagnostic evidence. Preserve tests, user work and recorded history. Deliver the actual results and reviewable diff to [development-handoff](../development-handoff/SKILL.md).
