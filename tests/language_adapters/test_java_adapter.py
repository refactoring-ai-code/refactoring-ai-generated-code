"""F04-JAVA acceptance tests against the real JavaParser Symbol Solver helper.

Acceptance criteria (issue #14):
  AC1 overloads map to correct symbols and Monaco source positions
  AC2 unknown and mixed-language files are not silently parsed as Java
  AC3 ambiguous references retain uncertainty
  AC4 capabilities distinguish analysis from safe_patch
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import ROOT, scope_for

from backend.core.schemas.adapter import require_capability
from backend.core.schemas.models import AdapterRequest
from backend.core.schemas.validation import ContractViolation, validate_bundle
from backend.language_adapters.analysis import (
    SnapshotIntegrityError,
    analyze_snapshot,
    analyze_version,
)
from backend.language_adapters.coordinates import SourceText, monaco_range, scalar_slice
from backend.language_adapters.java.adapter import JavaSymbolAdapter

ASTRAL = "\U0001F600"
FRAKTUR = "\U0001D518"  # astral letter, valid in Java identifiers

SHAPES = (
    b"package demo;\n\n"
    b"public class Shapes {\n"
    b"\tpublic static int area(int side) { return side * side; }\n"
    b"\tpublic static int area(int w, int h) { return w * h; }\n"
    b"\tpublic static double area(double radius) { return Math.PI * radius * radius; }\n"
    b"\tpublic static int bigger(int x) { return Math.max(x, 0); }\n"
    b"\tpublic Shapes() { this(1); }\n"
    b"\tpublic Shapes(int scale) { }\n"
    b"}\n"
)
APP = (
    "package demo;\r\n\r\n"
    f"/** {ASTRAL} astral text before code */\r\n"
    "public class App {\r\n"
    f'\tString label = "{ASTRAL}{ASTRAL}";\tint a = Shapes.area(2);\r\n'
    f"\tint {FRAKTUR}mfang() {{ return 4; }}\r\n"
    f'\tint run() {{ String s = "{FRAKTUR}"; int b = Shapes.area(2, 3); '
    f"double c = Shapes.area(1.5); return a + b + {FRAKTUR}mfang(); }}\r\n"
    "\tShapes make() { return new Shapes(); }\r\n"
    "}\r\n"
).encode()


def records(result, kind):
    return [record for record in result.bundle.records if record.kind == kind]


def index(result):
    return {record.id: record for record in result.bundle.records}


def call_sites(result, path):
    """Call-site locations (bound to a target symbol or unresolved) in one file."""
    declared = {symbol.location_id for symbol in records(result, "Symbol")}
    return [loc for loc in records(result, "SourceLocation")
            if loc.path == path and loc.id not in declared]


# ---------------------------------------------------------------------------- AC1
def test_overloads_bind_to_their_exact_declarations_and_monaco_positions(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES,
                                              "src/main/java/demo/App.java": APP})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    entities = index(result)
    symbols = {symbol.signature: symbol for symbol in records(result, "Symbol")}
    overloads = ["demo.Shapes.area(int)", "demo.Shapes.area(int, int)", "demo.Shapes.area(double)"]
    assert all(symbols[name].resolution == "RESOLVED" for name in overloads)
    assert len({symbols[name].location_id for name in overloads}) == 3

    shapes_text = SourceText.decode(SHAPES)
    for name, prefix in zip(overloads, ["public static int area(int side)",
                                        "public static int area(int w, int h)",
                                        "public static double area(double radius)"]):
        location = entities[symbols[name].location_id]
        assert scalar_slice(shapes_text, location.start_line, location.start_column,
                            location.end_line, location.end_column).startswith(prefix)

    app_text = SourceText.decode(APP)
    bound = {}
    for location in call_sites(result, "src/main/java/demo/App.java"):
        target = entities[location.symbol_id] if location.symbol_id else None
        text = scalar_slice(app_text, location.start_line, location.start_column,
                            location.end_line, location.end_column)
        bound[(location.start_line, text)] = target.signature if target else None
    assert bound[(5, "area")] == "demo.Shapes.area(int)"           # field initialiser
    calls_line_7 = sorted((loc.start_column, entities[loc.symbol_id].signature)
                          for loc in call_sites(result, "src/main/java/demo/App.java")
                          if loc.start_line == 7 and loc.symbol_id)
    assert [signature for _, signature in calls_line_7] == [
        "demo.Shapes.area(int, int)", "demo.Shapes.area(double)", f"demo.App.{FRAKTUR}mfang()"]
    assert bound[(8, "Shapes")] == "demo.Shapes.Shapes()"

    # Scalar columns differ from UTF-16 after astral characters; Monaco gets UTF-16.
    line5 = app_text.lines[4]
    area = next(loc for loc in call_sites(result, "src/main/java/demo/App.java")
                if loc.start_line == 5)
    assert area.start_column == line5.index("area") + 1
    monaco = monaco_range(app_text, area.start_line, area.start_column,
                          area.end_line, area.end_column)
    assert monaco["startColumn"] == area.start_column + 2  # two emoji before the call
    assert monaco["endColumn"] - monaco["startColumn"] == 4

    edges = {(entities[e.from_symbol_id].signature, entities[e.to_symbol_id].signature)
             for e in records(result, "DependencyEdge") if e.resolution == "RESOLVED"}
    assert ("demo.App.run()", "demo.Shapes.area(int, int)") in edges
    assert ("demo.App.a", "demo.Shapes.area(int)") in edges  # field initialiser call
    assert ("demo.Shapes.Shapes()", "demo.Shapes.Shapes(int)") in edges  # this(1)
    validate_bundle(result.bundle.model_dump(mode="json"))


def test_external_and_implicit_targets_are_resolved_without_invented_locations(snapshot,
                                                                              java_adapter):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES,
                                              "src/main/java/demo/App.java": APP})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    entities = index(result)
    external = [s for s in records(result, "Symbol")
                if s.signature == "java.lang.Math.max(int, int)"]
    assert len(external) == 1 and "outside the analysed snapshot" in external[0].reason
    edge = next(e for e in records(result, "DependencyEdge") if e.to_symbol_id == external[0].id)
    assert edge.resolution == "RESOLVED"
    assert entities[edge.from_symbol_id].signature == "demo.Shapes.bigger(int)"
    for symbol in records(result, "Symbol"):
        location = entities[symbol.location_id]
        if location.resolution == "UNRESOLVED":
            assert symbol.resolution == "UNRESOLVED" and symbol.reason
            assert location.start_line is None and location.reason


# ---------------------------------------------------------------------------- AC2
class SpyAdapter(JavaSymbolAdapter):
    seen: list[str]

    def run(self, root, paths):
        self.seen = list(paths)
        return super().run(root, paths)


def test_mixed_and_unknown_files_are_never_sent_to_the_java_parser(snapshot, helper_jar):
    files = {
        "app/pom.xml": b"<project/>",
        "app/src/main/java/a/Main.java": b"package a;\npublic class Main { void m() {} }\n",
        "app/src/main/java/a/script.py": b"class Main:\n    pass\n",
        "web/package.json": b"{}",
        "web/index.ts": b"export class Main {}\n",
        "notes/Snippet.java.txt": b"public class NotJava {}\n",
        "data/blob.dat": b"class Hidden {}\n",
    }
    root, manifest, digest, scope = snapshot(files)
    spy = SpyAdapter(helper_jar=helper_jar)
    result = analyze_snapshot(root, manifest, digest, scope, adapter=spy, selected_language="java")
    assert spy.seen == ["app/src/main/java/a/Main.java"]
    symbol_paths = {index(result)[s.location_id].path for s in records(result, "Symbol")}
    assert symbol_paths == {"app/src/main/java/a/Main.java"}
    declarations = {c.language: c for c in records(result, "LanguageAdapterCapabilities")}
    assert declarations["JAVA"].implementation_state == "RUNTIME_IMPLEMENTED"
    for language in ("PYTHON", "TYPESCRIPT"):
        assert declarations[language].implementation_state == "CONTRACT_DEFINED"
    statuses = {item["path"]: item["status"] for item in result.report["routing"]["files"]}
    assert statuses["notes/Snippet.java.txt"] == statuses["data/blob.dat"] == "UNKNOWN_LANGUAGE"
    assert statuses["app/src/main/java/a/script.py"] == "UNSUPPORTED_LANGUAGE"
    assert result.report["routing"]["mixed_language"] is True


def test_snapshot_with_only_unknown_files_produces_no_java_analysis(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"README": b"text", "a/b.cfg": b"k=v"})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    assert result.bundle is None and result.report["java_run"]["status"] == "NOT_RUN"
    assert {item["status"] for item in result.report["routing"]["files"]} == {"UNKNOWN_LANGUAGE"}


# ---------------------------------------------------------------------------- AC3
AMBIGUOUS = (
    b"package demo;\n"
    b"import com.missing.Lib;\n"
    b"public class Picker {\n"
    b"    void pick(String s) {}\n"
    b"    void pick(Integer i) {}\n"
    b"    void use() { pick(null); pick(\"x\"); Lib.call(); }\n"
    b"}\n"
)


def test_ambiguous_and_missing_references_stay_unresolved_with_reasons(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"src/demo/Picker.java": AMBIGUOUS})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    entities = index(result)
    edges = records(result, "DependencyEdge")
    unresolved = [e for e in edges if e.resolution == "UNRESOLVED"]
    ambiguous = [e for e in unresolved if e.reason.startswith("AMBIGUOUS")]
    missing = [e for e in unresolved if e.reason.startswith("MISSING_DEPENDENCY")]
    assert len(ambiguous) == 1 and ambiguous[0].to_symbol_id is None
    assert "demo.Picker.pick(java.lang.Integer)" in ambiguous[0].reason
    assert "demo.Picker.pick(java.lang.String)" in ambiguous[0].reason
    assert len(missing) == 1 and "Lib" in missing[0].reason
    resolved = [entities[e.to_symbol_id].signature for e in edges if e.resolution == "RESOLVED"]
    assert resolved == ["demo.Picker.pick(java.lang.String)"]  # pick("x") is not ambiguous
    # The call site keeps its exact location but is bound to no symbol.
    text = SourceText.decode(AMBIGUOUS)
    sites = [loc for loc in records(result, "SourceLocation")
             if loc.resolution == "RESOLVED" and loc.symbol_id is None]
    assert sorted(scalar_slice(text, s.start_line, s.start_column, s.end_line, s.end_column)
                  for s in sites) == ["call", "pick"]
    dependency = next(c for c in records(result, "Capability") if c.capability == "dependency")
    assert dependency.confidence.value == pytest.approx(1 / 3, abs=1e-6)
    assert not any("void pick" in (e.reason or "") for e in edges)  # no raw source in reasons


# ------------------------------------------------------------------ invalid source
def test_invalid_source_is_reported_and_does_not_block_other_files(snapshot, java_adapter):
    files = {"src/demo/Broken.java": b"package demo;\nclass Broken { void x( { }\n",
             "src/demo/Good.java": b"package demo;\npublic class Good { int v() { return 1; } }\n"}
    root, manifest, digest, scope = snapshot(files)
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    reports = {item["path"]: item for item in result.report["files"]}
    assert reports["src/demo/Broken.java"]["status"] == "PARSE_ERROR"
    assert reports["src/demo/Broken.java"]["problems"]
    assert all(p["range"] is None or len(p["range"]) == 4
               for p in reports["src/demo/Broken.java"]["problems"])
    assert reports["src/demo/Good.java"]["status"] == "PARSED"
    paths = {index(result)[s.location_id].path for s in records(result, "Symbol")}
    assert paths == {"src/demo/Good.java"}
    parse = next(c for c in records(result, "Capability") if c.capability == "parse")
    assert parse.status == "SUPPORTED" and parse.confidence.value == 0.5


def test_standalone_cr_source_keeps_symbols_but_no_guessed_coordinates(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot(
        {"src/demo/OldMac.java": b"package demo;\rpublic class OldMac {\r void m() {} }\r"})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    entities = index(result)
    symbols = records(result, "Symbol")
    assert {s.signature for s in symbols} >= {"demo.OldMac", "demo.OldMac.m()"}
    for symbol in symbols:
        location = entities[symbol.location_id]
        assert location.resolution == "UNRESOLVED" and "standalone CR" in location.reason
        assert symbol.resolution == "UNRESOLVED"


# ---------------------------------------------------------------------------- AC4
def _request(result, capability):
    declaration = next(c for c in records(result, "LanguageAdapterCapabilities")
                       if c.language == "JAVA")
    record = next(c for c in records(result, "Capability")
                  if c.capability == capability and c.component_id == declaration.component_id)
    return AdapterRequest(schema_version="1.0.0", scope=result.bundle.scope, language="JAVA",
                          component_id=declaration.component_id,
                          adapter_capabilities_id=declaration.id, capability_id=record.id,
                          operation=capability, input_artifact_id=result.bundle.artifacts[0].id,
                          timeout_seconds=60)


def test_capability_guard_allows_analysis_and_rejects_safe_patch(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES})
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    states = {c.capability: c for c in records(result, "Capability")}
    assert {name for name, c in states.items() if c.status == "SUPPORTED"} == {
        "parse", "symbol", "dependency"}
    for name in ("quality", "build", "test", "coverage", "safe_patch", "security"):
        assert states[name].status == "NOT_IMPLEMENTED" and states[name].reason
        assert states[name].tool is None and not states[name].evidence_ids
    assert "safe_patch" in states["safe_patch"].reason
    assert states["symbol"].tool.version.startswith("3.28.2")
    for name in ("parse", "symbol", "dependency"):
        assert require_capability(_request(result, name), result.bundle).capability == name
    for name in ("safe_patch", "build", "test"):
        with pytest.raises(ContractViolation) as error:
            require_capability(_request(result, name), result.bundle)
        assert error.value.code == "UNAVAILABLE_CAPABILITY"


def test_missing_toolchain_is_unavailable_not_supported(snapshot, tmp_path):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES})
    adapter = JavaSymbolAdapter(helper_jar=tmp_path / "absent.jar")
    result = analyze_snapshot(root, manifest, digest, scope, adapter=adapter)
    states = {c.capability: c for c in records(result, "Capability")}
    assert {states[n].status for n in ("parse", "symbol", "dependency")} == {"UNAVAILABLE"}
    assert "not built" in states["parse"].reason
    declaration = records(result, "LanguageAdapterCapabilities")[0]
    assert declaration.implementation_state == "CONTRACT_DEFINED"
    assert not records(result, "Symbol")


# ------------------------------------------------------------------- V0 integrity
def test_modified_copy_or_mismatched_scope_is_rejected_before_parsing(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES})
    with pytest.raises(ContractViolation):
        analyze_snapshot(root, manifest, digest, scope_for("1" * 64), adapter=java_adapter)
    (root / "src/main/java/demo/Shapes.java").write_bytes(SHAPES + b"// tampered\n")
    spy = SpyAdapter(helper_jar=java_adapter.helper_jar)
    with pytest.raises(SnapshotIntegrityError):
        analyze_snapshot(root, manifest, digest, scope, adapter=spy)
    assert not hasattr(spy, "seen")


PILOT = "experiments/original-ai-code/java-inventory-v0"
INTEGRITY = "experiments/java-pilot/verify_integrity.py"


def _sha256_tree(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def test_java_pilot_v0_is_analysed_from_a_copy_and_stays_byte_identical(snapshot, java_adapter):
    sealed = sorted(p for d in (ROOT / PILOT, ROOT / "tests/fixtures/java-inventory-v0")
                    for p in d.rglob("*") if p.is_file())
    before = _sha256_tree(sealed)
    check = [sys.executable, "-B", str(ROOT / INTEGRITY)]
    assert subprocess.run(check, cwd=ROOT, capture_output=True, check=False).returncode == 0
    files = {p.relative_to(ROOT / PILOT).as_posix(): p.read_bytes()
             for p in (ROOT / PILOT).rglob("*") if p.is_file()}
    root, manifest, digest, scope = snapshot(files)
    result = analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    entities = index(result)
    signatures = {s.signature for s in records(result, "Symbol") if s.resolution == "RESOLVED"}
    assert {"org.genesis.pilot.Inventory",
            "org.genesis.pilot.Inventory.availableStock(java.lang.String)",
            "org.genesis.pilot.Inventory.placeOrder(java.lang.String, int)",
            "org.genesis.pilot.Inventory.requireItemId(java.lang.String)",
            "org.genesis.pilot.Inventory.OrderReceipt"} <= signatures
    edges = {(entities[e.from_symbol_id].signature, entities[e.to_symbol_id].signature)
             for e in records(result, "DependencyEdge") if e.resolution == "RESOLVED"}
    assert ("org.genesis.pilot.Inventory.placeOrder(java.lang.String, int)",
            "org.genesis.pilot.Inventory.availableStock(java.lang.String)") in edges
    receipt = [entities[e.to_symbol_id] for e in records(result, "DependencyEdge")
               if e.resolution == "RESOLVED"
               and entities[e.to_symbol_id].name == "OrderReceipt"]
    assert receipt and "implicit" in receipt[0].reason  # record canonical constructor
    assert _sha256_tree(sealed) == before
    assert subprocess.run(check, cwd=ROOT, capture_output=True, check=False).returncode == 0


# ------------------------------------------------------- real F03 V0 integration
def test_analysis_reads_an_owner_v0_through_the_f03_snapshot_store(tmp_path, java_adapter):
    from backend.core.workflow import Mutation
    from backend.storage.database import migrate_state, state_engine
    from backend.storage.input_validation import Intake
    from backend.storage.source_snapshots import Policy, SourceSnapshots

    engine = state_engine(tmp_path / "state.db")
    migrate_state(engine)
    intake = Intake()
    for path, data in {"src/main/java/demo/Shapes.java": SHAPES,
                       "src/main/java/demo/App.java": APP, "tools/run.py": b"print(1)\n"}.items():
        intake.add_bytes(intake.register(path), data)
    store = SourceSnapshots(engine)
    decisions = {"terms": True, "retention": True, "cloud_transmission": False,
                 "dynamic_execution": False}
    created = store.create(intake.finish(), "folder", "java", decisions,
                           Policy({k: f"{k}.v1" for k in decisions}, 1),
                           Mutation("actor:owner", "f04-intake"))
    scope = scope_for(created["manifest_sha256"], created["version_id"]).model_copy(
        update={"project_id": created["project_id"]})
    before = store.download("actor:owner", created["version_id"])
    result = analyze_version(store, "actor:owner", created["version_id"], scope,
                             adapter=java_adapter)
    assert result.bundle.scope.baseline_sha256 == created["manifest_sha256"]
    assert {f.path for f in result.bundle.files} == {
        "src/main/java/demo/Shapes.java", "src/main/java/demo/App.java", "tools/run.py"}
    assert any(s.signature == "demo.Shapes.area(int, int)" for s in records(result, "Symbol"))
    assert store.download("actor:owner", created["version_id"]) == before
    with pytest.raises(ContractViolation):
        analyze_version(store, "actor:owner", created["version_id"],
                        scope.model_copy(update={"project_id": "project:other"}),
                        adapter=java_adapter)


def test_analysis_never_writes_into_the_derived_copy(snapshot, java_adapter):
    root, manifest, digest, scope = snapshot({"src/main/java/demo/Shapes.java": SHAPES})
    before = {p.relative_to(root): p.read_bytes() for p in Path(root).rglob("*") if p.is_file()}
    analyze_snapshot(root, manifest, digest, scope, adapter=java_adapter)
    after = {p.relative_to(root): p.read_bytes() for p in Path(root).rglob("*") if p.is_file()}
    assert after == before
