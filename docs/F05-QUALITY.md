# F05-QUALITY Java quality analysis

[F05-QUALITY (#15)](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/15)
adds PMD and CPD quality measurements to Java analysis. The F03 storage-backed
analysis entry point runs both tools on the verified V0 derivative, using only
the Java manifest paths in each routed component. The analyzer does not compile,
load, or run uploaded code. JavaParser capability and quality capability have
independent execution evidence.

## Tool and rules

Use Java 21 and the pinned PMD/CPD 7.29.0 distribution. Install the verified
tools from the repository root:

```text
uv run --project backend --locked python -m backend.analyzers.quality.distribution
```

The installer validates the release archive against SHA-256
`d27177c185b837fa57f097e482d1253468aa035379c5eb2671fa0a279109b179`
before extracting JVM libraries into the ignored quality cache. A separately
downloaded copy of the same official archive can be supplied with
`--archive <path>`. The runtime uses an allowlisted environment, English JVM
locale, UTF-8 and a bounded execution timeout.

| Source category | Rule | CIR category |
|---|---|---|
| PMD Design | CyclomaticComplexity | COMPLEXITY |
| PMD Best Practices | UnusedLocalVariable | QUALITY |
| PMD Error Prone | EmptyCatchBlock | QUALITY |
| PMD Code Style | ClassNamingConventions | QUALITY |
| CPD Duplication | Java match with at least 50 tokens | DUPLICATION |

PMD emits native XML. The CPD API renderer writes its real match and error
records with manifest-relative paths. Both XML reports are retained by digest under
`.cache/reports/<sha256>.xml`. The CIR artifact contains the report SHA-256,
media type and review state. Raw reports may contain source text. Keep them
inside the authorized analysis environment. Structured results carry safe
status messages and opaque artifact references.

Reported paths must match manifest entries and resolve against verified source.
Ranges use one-based Unicode scalar columns and an exclusive end. Invalid
coordinates stay unresolved. A CPD finding preserves all occurrences in its
group. Stable finding identity includes the tool, rule and source locations.
Resolved PMD and CPD ranges that overlap link to each other's independent
evidence while retaining their distinct rules.

## Metrics and comparison

| Metric | Unit | Formula within one routed Java component |
|---|---|---|
| pmd_finding_count | COUNT | Number of distinct PMD rule and location observations |
| cpd_duplicate_token_count | COUNT | Sum of CPD XML tokens over distinct duplication groups |
| cpd_duplicate_line_count | COUNT | Sum of CPD XML lines over distinct duplication groups |

The two CPD formulas count each report group once. They can include overlapping
groups and do not measure unique duplicated source or a duplication percentage.
The Java quality scope does not use coverage or a test-suite denominator.

Every metric records tool version, configuration digest, rule definition,
logical path scope and JVM fingerprint using CIR 1.0.0. Measurement scope
excludes changing file content. Changes to the comparison key or unmeasured
values yield NOT_COMPARABLE. A completed empty scan yields a measured zero.
An incomplete or unavailable scan yields unavailable metrics with a reason.
Both successful tool reports are required to declare the Java quality
capability supported. SonarQube is optional and outside this implementation.

## Verification

```text
uv run --project backend --locked ruff check --config backend/pyproject.toml backend/analyzers backend/language_adapters tests/language_adapters
uv run --project backend --locked python -m pytest -c backend/pyproject.toml --rootdir . tests/language_adapters -ra
python -B experiments/java-pilot/verify_integrity.py
```

The quality tests require the pinned tools and a real scan. The complete
command results and hosted CI status are in [the task report](../report.md).
The [documentation index](README.md) lists the other project guides.
