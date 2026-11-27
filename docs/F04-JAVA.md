# F04-JAVA language router and Java symbol adapter

[Issue #14](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/14)
implements FR-008 (per-file/component language routing), FR-010 (Java symbols,
overloads, source ranges and uncertain references through JavaParser Symbol Solver)
and FR-011 (independent capability declarations). It consumes the
[F03-INPUT](F03-INPUT.md) canonical manifest and immutable V0, and produces CIR 1.0.0
records validated by the [F02 contract](contracts/SEMANTICS.md) `validate_bundle`.

Quality measurement (F05-QUALITY), sandboxed build/test/coverage (F06-SANDBOX),
security scanning (F07A-SCAN), patching and the other language adapters remain with
their own tasks. F04 never compiles, class-loads or executes uploaded source.

## Components

| Module | Responsibility |
|---|---|
| [`router.py`](../backend/language_adapters/router.py) | Route every manifest file; split components by build root and language |
| [`java/helper`](../backend/language_adapters/java/helper/pom.xml) | Java 21/Maven helper using `javaparser-symbol-solver-core` 3.28.2 |
| [`java/adapter.py`](../backend/language_adapters/java/adapter.py) | Run the helper in a bounded subprocess; build CIR records |
| [`coordinates.py`](../backend/language_adapters/coordinates.py) | JavaParser UTF-16 → CIR scalar → Monaco UTF-16 conversion |
| [`capabilities.py`](../backend/language_adapters/capabilities.py) | Nine Capability records plus `LanguageAdapterCapabilities` |
| [`analysis.py`](../backend/language_adapters/analysis.py) | `analyze_version` / `analyze_snapshot` entry points |

## Routing (FR-008)

Every file in the manifest receives one explicit status. Nothing is parsed by
guessing:

- `ROUTED`: an implemented runtime adapter analyses the file. Today only Java
  (`adapter:java-javaparser`).
- `UNSUPPORTED_LANGUAGE`: the language is recognised (Python, JS/TS, C#, Go, C++, C)
  but has no runtime adapter yet. The pending task is named. Its component still gets
  a `CONTRACT_DEFINED` capability declaration with nine `NOT_IMPLEMENTED` records.
- `UNKNOWN_LANGUAGE`: the file has no recognised source extension (for example
  `Snippet.java.txt`, `pom.xml`, `README`). It is never sent to any parser.

Components are `(build root, language)` pairs. The build root is the deepest
directory that holds a build descriptor (`pom.xml`, `build.gradle`, `package.json`,
`pyproject.toml`, `go.mod`, `*.csproj`, `CMakeLists.txt` …). Without one, the
snapshot root is used. A mixed project therefore yields one component per language.

The user's `selected_language` is a hint. It never re-routes a file whose language F03
detected. Conflicts are listed in `hint_mismatches`. The hint only labels `.h` headers,
which F03 reports as `unknown`, and such a header still is not parsed.

## Java symbol analysis (FR-010)

`analyze_version` obtains a verified temporary copy through
`SourceSnapshots.workspace`, which re-verifies V0 afterwards. `analyze_snapshot` then
re-checks each file's size and SHA-256 against the manifest before anything is parsed.

The helper parses with language level Java 21, tab size 1 and no Unicode-escape
preprocessing. It resolves types in two layers:

- JRE types through `ReflectionTypeSolver(jreOnly)`.
- Project types through `JavaParserTypeSolver`, rooted at package-derived source roots.

Third-party libraries are deliberately not resolved. The helper runs with
`Locale.ROOT`. On a Turkish-locale JVM, JavaParser otherwise lower-cases `INT` to
`ınt` and corrupts every primitive signature; this was observed during development.

| Output | CIR representation |
|---|---|
| Type, method, constructor, field declarations | `Symbol` with qualified signature (each overload distinct), `public_api`, declaration `SourceLocation` bound via `symbol_id` |
| Method/constructor/`this`/`super` calls | Call-site `SourceLocation` on the called name, bound to the exact target overload; `DependencyEdge` `CALL` from the enclosing declaration |
| JDK or implicit targets (for example a record's canonical constructor) | `Symbol` with `UNRESOLVED` location and an explicit reason; the edge itself stays `RESOLVED` |
| Ambiguous overload (`pick(null)`) | `DependencyEdge` `UNRESOLVED`, `AMBIGUOUS: …` reason with the arity-compatible candidate signatures |
| Missing dependency | `UNRESOLVED`, `MISSING_DEPENDENCY: unsolved symbol: <name>` |
| Syntax error | File reported as `PARSE_ERROR` with converted problem ranges; other files continue |

Reasons carry identifiers and failure classes only. They never carry the solver's raw
source fragments.

### Coordinates

CIR ranges are 1-based, start-inclusive, end-exclusive and counted in Unicode scalar
values. JavaParser reports 1-based UTF-16 columns with an inclusive end. Conversion
uses the original V0 bytes:

- CRLF and LF each end one line.
- A tab counts as one column.
- An astral character counts as one scalar column but two UTF-16 columns.
- An inclusive end on either half of a surrogate pair covers the whole character.

Each converted declaration range is verified twice. First, its converted name range
must slice to the declared name. Second, it must pass the F02 `source_offsets` check.
Files with a standalone CR or invalid UTF-8 keep their symbols with `UNRESOLVED`
locations rather than guessed coordinates. `monaco_range` mirrors
`frontend/src/coordinates.ts`. A test runs that TypeScript module through Node and
compares its output on CRLF, tab and astral text.

## Capability manifest (FR-011)

| Capability | Java status | Evidence / reason |
|---|---|---|
| `parse`, `symbol`, `dependency` | `SUPPORTED` when the helper ran | Verified deterministic-tool evidence; confidence is the observed parsed-file, resolved-declaration and resolved-reference ratio |
| `quality` | `NOT_IMPLEMENTED` | F05-QUALITY (#15) |
| `build`, `test`, `coverage` | `NOT_IMPLEMENTED` | Require F06-SANDBOX (#16); F04 never compiles or runs uploads |
| `safe_patch` | `NOT_IMPLEMENTED` | F10-PATCH (#25) and F11-VALIDATE (#26); analysis does not imply safe patching |
| `security` | `NOT_IMPLEMENTED` | F07A-SCAN (#18) |

If Java or the helper jar is missing, `parse`, `symbol` and `dependency` become
`UNAVAILABLE` with a reason, and the component stays `CONTRACT_DEFINED`.
`require_capability` accepts `parse`, `symbol` and `dependency` requests and rejects
`safe_patch`, `build` and `test` with `UNAVAILABLE_CAPABILITY`.

## Build and verify

Requirements: Java 21 (Temurin), Maven 3.9.11 and Maven Central access for the first
build. The build adds one runtime dependency, `com.github.javaparser:
javaparser-symbol-solver-core:3.28.2`, packaged into a shaded jar under the ignored
`target/` directory. Set `GENESIS_JAVA_HELPER_JAR` to use a prebuilt jar.

```text
mvn -B -q -DskipTests -f backend/language_adapters/java/helper/pom.xml package
uv run --project backend --locked python -m pytest -c backend/pyproject.toml --rootdir . tests/language_adapters
```

If the jar is absent, the test fixture builds it. A missing Java runtime fails the
suite rather than skipping it. The only conditional skip is the Monaco cross-check,
which needs Node.js ≥ 22.18 for TypeScript type stripping.

### Results recorded on 2026-11-27 (Windows 11, Temurin 21.0.13.1, Maven 3.9.11, Node 26)

| Check | Result |
|---|---|
| `tests/language_adapters` (27 tests, 0 skipped) | PASS |
| `ruff check` on the new packages (backend configuration) | PASS |
| `backend-checks` commands (`ruff` + `pytest backend/tests`) | ruff PASS; pytest 38/39. The failing `dir\file.txt` case also fails on unmodified `main` `eb0a6d3` on Windows (a backslash is a path separator there); it is unrelated to F04 |
| `governance-tests` | 81/83. Two symlink tests error on unmodified `main` on Windows without symlink privilege; unrelated to F04 |
| `documentation-checks`, `security-checks` | PASS |
| `contract-checks` (`run_checks.py`, `export --check`) | PASS (55 tests; exports current) |
| Java pilot `verify_integrity.py` before/after, `reproduce.py` | PASS; 10/10 JUnit tests; V0 and fixed-test hashes unchanged |

**CI gap.** The current `backend-checks` workflow runs only `pytest backend/tests` and
installs no JDK, so these adapter tests do not run in hosted CI from this task's
allowed paths. Connecting them needs a workflow change outside F04's scope. It is
proposed through governance (F01-GOV) as a separate PR.

## Limitations

- Only `CALL` edges are produced. `READ`, `WRITE`, `INHERIT` and `IMPORT` edges are not.
- Method references, lambdas' functional targets and local variables are not modelled.
- Ambiguity candidates are same-name, arity-compatible declarations in the analysed
  sources. They are not the solver's internal candidate list.
- Generated sources, annotation processors and Maven dependency resolution are out of
  scope. Library calls therefore remain `MISSING_DEPENDENCY`.
