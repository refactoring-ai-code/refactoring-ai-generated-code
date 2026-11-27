# Experiments

This directory contains the experimental work conducted during the project.

It will include AI-generated code samples, refactored versions of the code,
and materials used to compare software quality before and after refactoring.

## Research protocol and current evidence

Use the single [F00 research baseline and evidence protocol](../docs/DECISIONS/0005-f00-research-baseline.md)
for task admission, the minimum twelve-task dataset, immutable V0/tests,
dataset freeze, three matched sequential/parallel repetitions, measurement
denominators and resource decisions.

At the inspected baseline `67233482f2d10462933328c4b162d150bb4b0993`, these
directories contain README scaffolds only: dataset **NOT_FROZEN**, Java pilot
**NOT_STARTED**, research executions **NOT_RUN**. The 50% finding-reduction
threshold is an experimental target, not a measured result. Actual Java pilot
work belongs to F00-V0 (#9); comparative execution belongs to F15-EXPERIMENT (#36).

## F00-V0 local implementation — 2026-11-03

The [Java inventory/order pilot](java-pilot/README.md) now has generated Java 21
source, a pinned Maven build, external JUnit tests, attributable generation
records and separate raw-byte source/test manifests. Its local build and
temporary-copy reproduction passed ten tests each. This is a local task
snapshot pending human publication, hosted CI and Burkay's exact-HEAD approval;
the earlier paragraph records the historical baseline. The twelve-task dataset
remains NOT_FROZEN, comparative research NOT_RUN and release NOT_READY.

Publication update: [PR #45](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/45)
was merged on 2026-11-04 at `fdd573286834fe15c1ac1c0d51db4ed9b0015db7` from source
`d923134da4f9f5a2ab55a5f51fbf9415ff717262`, and F00-V0 (#9) was accepted the same day
(see the [acceptance registry](../.github/acceptance.json)). The
[publication evidence](java-pilot/evidence/publication-checks.json) records the
pre-merge revision checks. The pilot source and fixed tests are the frozen V0
baseline. The twelve-task research dataset remains NOT_FROZEN and comparative
research NOT_RUN; the earlier paragraphs are historical snapshots.
