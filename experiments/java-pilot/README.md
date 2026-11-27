# Java inventory/order pilot — F00-V0

This is the bounded `java-inventory-v0.1` synthetic AI-generated pilot, not the
refactoring platform or a completed twelve-task study. It uses Java 21 and Maven
3.9.11, with no production dependency. JUnit 5.12.2 is test-only. The original
production output is [Inventory.java](../original-ai-code/java-inventory-v0/src/main/java/org/genesis/pilot/Inventory.java);
the [Maven descriptor](../original-ai-code/java-inventory-v0/pom.xml) loads the
[external fixed tests](../../tests/fixtures/java-inventory-v0/src/test/java/org/genesis/pilot/InventoryTest.java).

## Observable behavior

`new Inventory(initialStock)` copies a map of exact, case-sensitive item IDs to
non-negative integer quantities. Null/blank IDs and null/negative stock are
rejected. `availableStock(id)` reads stock. `placeOrder(id, quantity)` accepts
positive quantities up to available stock and returns an immutable
`OrderReceipt(itemId, quantity, remainingStock)`. Invalid quantities, invalid
IDs and unknown items throw `IllegalArgumentException`; insufficient stock
throws `IllegalStateException`. Rejections preserve stock. This single-threaded
example has no database, UI, network, secrets, external user data or persistence.

## Reproduce without changing the original

Run from the repository root with Python 3 standard library, Java 21 and Maven
3.9.11 on PATH:

```sh
java -version
mvn -version
python3 -B experiments/java-pilot/verify_integrity.py
python3 -B experiments/java-pilot/reproduce.py
```

If Maven is user-local, pass its executable explicitly:

```sh
python3 -B experiments/java-pilot/reproduce.py --maven "$HOME/.local/share/project-genesis/apache-maven-3.9.11/bin/mvn"
```

`reproduce.py` checks tool versions and both manifests, copies only their inputs
to an automatically removed temporary derivative, then executes:

```sh
mvn -B -ntp -f experiments/original-ai-code/java-inventory-v0/pom.xml clean verify
```

The Maven command runs from the derivative root. The helper checks the
derivative and original hashes after execution, parses actual Surefire XML and
requires all ten fixed tests with zero failures/errors/skips. It prints the JAR
hash and individual test names. Surefire also fails when no tests are found.
Do not pass skip flags or build later patches in the original source directory.
Maven needs HTTPS access to Maven Central to resolve the pinned plugins and
JUnit on a machine without a dependency cache. This is a controlled local
execution of this owner-authorized synthetic pilot, not an implemented sandbox
for untrusted uploads or permission to execute arbitrary third-party projects.

## Tool setup and verified versions

The recorded local environment is Temurin 21.0.4+7, Maven 3.9.11, macOS 26.6.2
(Darwin 25.6.0 arm64), and Python 3.14.3. See the actual command outputs in
[environment.json](evidence/environment.json); that artifact takes precedence
over this explanatory text. No global PATH or system package was changed.

Maven distribution:
<https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.11/apache-maven-3.9.11-bin.tar.gz>

Expected SHA-512 (verified against Maven Central before extraction):

```text
bcfe4fe305c962ace56ac7b5fc7a08b87d5abd8b7e89027ab251069faebee516b0ded8961445d6d91ec1985dfe30f8153268843c89aa392733d1a3ec956c9978
```

Download only that distribution, verify its raw bytes with `shasum -a 512`
(macOS) or `sha512sum` (Linux), and extract into a new user-owned directory after
the digest matches. Use an already compatible Java 21 installation. Official
references: [Maven release](https://maven.apache.org/docs/3.9.11/release-notes.html),
[JUnit guide](https://docs.junit.org/5.12.2/user-guide/).

The POM explicitly pins clean 3.4.1, resources 3.3.1, compiler 3.14.0, Surefire
3.5.3 and jar 3.4.2. The release target is Java 21; the archive timestamp is
fixed. Two builds on the recorded local environment produced identical JAR
bytes. This is not a claim of cross-platform byte reproducibility.

## Provenance and integrity

The [exact owner execution contract](provenance/execution-contract-02.txt),
[contemporaneous generation instruction](provenance/generation-prompt.txt),
and [attempt ledger](provenance/generation.json) identify one actual current
Codex source-generation attempt, `F00-V0-GEN-001`, with no source correction.
The original output is the source file itself, identified by its captured hash.
Provider is OpenAI; exact serving model ID, revision, sampling settings,
transport request ID and usage/cost are **UNKNOWN**, because this session does
not expose them. Do not treat agent-authored provenance as independent provider
attestation or claim complete model metadata.

[Source manifest](manifests/v0-source.json) covers production source, POM and
provenance; [test manifest](manifests/fixed-tests.json) covers the external fixed
test suite. Paths are sorted repository-relative paths, hashes cover actual raw
file bytes, and each manifest uses UTF-8 JSON with sorted keys, two-space
indentation and a final LF. Separate `.json.sha256` receipts hash the manifest
bytes; manifests never contain their own digest. Build output and evidence logs
are outside the frozen input inventories. The verifier rejects missing/extra
inputs, changed bytes, changed manifests and symlinks.

Status: the pilot V0 and fixed tests are **accepted and frozen**. PR #45 was merged
on 2026-11-04 and F00-V0 (#9) was accepted with this exact source revision. The
manifests still carry their original `seal_status` value
`LOCAL_SEALED_PENDING_OWNER_ACCEPTANCE`, because they are frozen bytes and are never
rewritten. Keep the receipts with the reviewed
revision: these unsigned hashes detect drift, not an adversary replacing both
files and receipts. Never refresh them merely to make a modified V0 pass.
Corrections require an attributable new baseline revision and owner decision.
The minimum twelve-task dataset remains **NOT_FROZEN**; no findings, quality
reduction, code coverage, analyzer result or research success is claimed here.

## Execution evidence and hosted CI

Command log artifacts encode the exact UTF-8 output as a JSON string with its
raw-byte SHA-256. Decode the `text` field as UTF-8 to reconstruct the original
bytes, including Maven's trailing spaces; output was not silently normalized.

- [Initial build record](evidence/initial-run.json) and [actual Maven log](evidence/maven-initial.log.json).
- [Temporary-copy reproduction result](evidence/reproduction.json) and [log](evidence/reproduction.log.json).
- [Integrity rejection probes](evidence/integrity-negative-probes.json), each on a fresh disposable derivative.
- [Deliberate regression rejection](evidence/regression-rejection.json): omitting the
  stock update in a disposable derivative caused real JUnit failures and Maven
  exit 1; original source/tests were not edited.
- [Final local checks](evidence/verification.json).

The [workflow](../../.github/workflows/pilot-checks.yml) defines the exact
`pilot-checks` job for all PRs targeting main and pushes to main, avoiding path
filters that could leave a required check missing. It uses pinned official
actions, read-only contents permission, no secrets/persistent credentials, a
ten-minute limit, Temurin 21.0.4+7 (`21.0.4+7.0.LTS` action syntax) and digest-verified Maven 3.9.11. It runs the
same temporary-copy reproduction and a final integrity check even on failure.
Hosted results must be observed after publication for the actual revision; old
main CI is not evidence for these files. Governance checks, owner approval,
merge and orchestrator acceptance remain separate requirements.

### Published execution evidence

[PR #45](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/45)
was merged on 2026-11-04 at `fdd573286834fe15c1ac1c0d51db4ed9b0015db7`. The paragraph
below records the pre-merge revision checks. [Hosted history](evidence/hosted-ci-history.json) retains the initial
setup-java version-resolution failure and exact one-line correction. At the
observed correction SHA `eae5d891e926ec12b87375023f33b813cc1c64a2`, the real
[pilot run](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687880387)
passed all ten JUnit tests and both manifest checks on Ubuntu. Governance jobs
and dependency-gate passed; merge-readiness failed for missing Burkay approval.
[Publication evidence](evidence/publication-checks.json) distinguishes the
observed source SHA, GitHub test-merge checkout and the later containing report
revision. The delegated approval, the merge-revision pilot and governance runs, and
the accepted handoff are recorded in the [acceptance registry](../../.github/acceptance.json)
entry for #9. The twelve-task research dataset is still not frozen.
