"""F05 acceptance: real PMD/CPD on owner snapshots and strict report boundaries."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from conftest import ROOT, scope_for

from backend.analyzers.quality.distribution import CACHE, VERSION, installed_libraries
from backend.analyzers.quality.normalize import (
    CPD_RULE,
    InvalidQualityReport,
    compare_quality_metrics,
    parse_report,
)
from backend.analyzers.quality.runner import QualityAnalyzer, ToolRun
from backend.core.schemas.models import Capability, Evidence, Finding, Metric, SourceLocation
from backend.core.schemas.validation import validate_bundle
from backend.core.workflow import Mutation
from backend.language_adapters.analysis import analyze_version
from backend.language_adapters.coordinates import SourceText, scalar_slice
from backend.language_adapters.java.adapter import JavaSymbolAdapter
from backend.storage.database import migrate_state, state_engine
from backend.storage.input_validation import Intake
from backend.storage.source_snapshots import Policy, SourceSnapshots

SOURCES = Path(__file__).with_name("sources")
PREFIX = "src/main/java/example/"
RULES = {
    "pmd/java/design/CyclomaticComplexity": "COMPLEXITY",
    "pmd/java/bestpractices/UnusedLocalVariable": "QUALITY",
    "pmd/java/errorprone/EmptyCatchBlock": "QUALITY",
    "pmd/java/codestyle/ClassNamingConventions": "QUALITY",
    CPD_RULE: "DUPLICATION",
}


@pytest.fixture(scope="module")
def quality_analyzer(tmp_path_factory):
    libraries = installed_libraries(CACHE)
    if libraries is None:
        pytest.fail("Install pinned PMD: python -m backend.analyzers.quality.distribution")
    cache = tmp_path_factory.mktemp("quality-report-cache")
    # Isolate retained XML from regular development evidence without copying tool binaries.
    analyzer = QualityAnalyzer(cache)
    return analyzer, libraries


@pytest.fixture
def analyze(tmp_path, monkeypatch):
    engine = state_engine(tmp_path / "state.db")
    migrate_state(engine)
    store = SourceSnapshots(engine)
    adapter = JavaSymbolAdapter(helper_jar=tmp_path / "java-helper-not-installed.jar")

    attempt = 0

    def use(files, analyzer, libraries=None):
        nonlocal attempt
        if libraries is not None:
            monkeypatch.setattr(
                "backend.analyzers.quality.runner.installed_libraries", lambda cache: libraries,
            )
        intake = Intake()
        for path, data in files.items():
            intake.add_bytes(intake.register(path), data)
        decisions = {"terms": True, "retention": True, "cloud_transmission": False,
                     "dynamic_execution": False}
        created = store.create(intake.finish(), "folder", "java", decisions,
                               Policy({key: f"{key}.v1" for key in decisions}, 1),
                               Mutation("actor:owner", f"f05-{attempt}"))
        attempt += 1
        version = created["version_id"]
        scope = scope_for(created["manifest_sha256"], version).model_copy(
            update={"project_id": created["project_id"]},
        )
        before = store.download("actor:owner", version)
        result = analyze_version(store, "actor:owner", version, scope, adapter=adapter,
                                 quality_analyzer=analyzer)
        assert store.download("actor:owner", version) == before
        assert validate_bundle(result.bundle.model_dump(mode="json")) == result.bundle
        return result

    return use


def records(result, record_type):
    return [item for item in result.bundle.records if isinstance(item, record_type)]


@pytest.fixture
def java_sources():
    return {PREFIX + source.name: source.read_bytes().replace(b"\n", b"\r\n")
            for source in sorted(SOURCES.glob("*.java"))}


def test_four_real_pmd_categories_and_two_cpd_counts(analyze, java_sources, quality_analyzer):
    analyzer, libraries = quality_analyzer
    result = analyze(java_sources, analyzer, libraries)
    repeated = analyze(java_sources, analyzer, libraries)
    findings = records(result, Finding)
    repeated_ids = {finding.id for finding in records(repeated, Finding)}
    assert {finding.id for finding in findings} == repeated_ids
    assert {record.rule_id: record.category for record in findings} == RULES
    evidence = {record.id: record for record in records(result, Evidence)}
    locations = {record.id: record for record in records(result, SourceLocation)}
    artifacts = {record.id: record for record in result.bundle.artifacts}
    for finding in findings:
        assert finding.tool.version == VERSION
        assert finding.tool.config_sha256
        assert finding.classification == "QUALITY_REFACTOR"
        assert finding.eligibility == "ELIGIBLE"
        assert all(locations[site].resolution == "RESOLVED" for site in finding.location_ids)
        proof = evidence[finding.evidence_ids[0]]
        assert proof.verification == "VERIFIED"
        assert proof.rule_id == finding.rule_id
        artifact = artifacts[proof.artifact_id]
        raw = (analyzer.cache / "reports" / f"{artifact.sha256}.xml").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == artifact.sha256
        if finding.rule_id.endswith("/UnusedLocalVariable"):
            position = locations[finding.location_ids[0]]
            assert scalar_slice(SourceText.decode(java_sources[position.path]),
                                position.start_line, position.start_column,
                                position.end_line, position.end_column) == "spare"
        if finding.rule_id == CPD_RULE:
            assert {locations[site].path for site in finding.location_ids} == {
                PREFIX + "FirstDuplicate.java", PREFIX + "SecondDuplicate.java",
            }
            for site in finding.location_ids:
                position = locations[site]
                segment = scalar_slice(
                    SourceText.decode(java_sources[position.path]), position.start_line,
                    position.start_column, position.end_line, position.end_column,
                )
                assert segment.startswith("{") and segment.endswith("}")
            related_rules = {evidence[item].rule_id for item in finding.evidence_ids[1:]}
            assert related_rules == {"pmd/java/bestpractices/UnusedLocalVariable"}

    metrics = {record.name: record for record in records(result, Metric)}
    tokens, lines = metrics["cpd_duplicate_token_count"], metrics["cpd_duplicate_line_count"]
    assert tokens.value >= 50 and 0 < lines.value < tokens.value
    assert tokens.unit == lines.unit == "COUNT"
    assert tokens.comparison_key != lines.comparison_key
    for metric in metrics.values():
        assert metric.subject_sha256 == result.bundle.scope.baseline_sha256
        assert metric.comparison.environment_sha256
        assert metric.comparison.measurement_scope_sha256
        assert metric.comparison.test_suite_state == "NOT_APPLICABLE"
        assert compare_quality_metrics(metric, metric) == "UNCHANGED"
    capability = next(cap for cap in records(result, Capability) if cap.capability == "quality")
    assert capability.status == "SUPPORTED"
    assert {evidence[item].tool.tool_id for item in capability.evidence_ids} == {"pmd", "cpd"}


def test_changed_scope_rules_and_tool_are_not_comparable(analyze, java_sources, quality_analyzer):
    analyzer, libraries = quality_analyzer
    result = analyze(java_sources, analyzer, libraries)
    subset = analyze({PREFIX + "BadQuality.java": java_sources[PREFIX + "BadQuality.java"]},
                     analyzer, libraries)
    baseline = next(
        metric for metric in records(result, Metric) if metric.name == "pmd_finding_count"
    )
    candidate = next(metric for metric in records(subset, Metric) if metric.name == baseline.name)
    old_tool = candidate.comparison.tool.model_copy(update={"version": "0.0.0"})
    assert compare_quality_metrics(baseline, candidate) == "NOT_COMPARABLE"
    for update in ({"tool": old_tool}, {"rule_set_version": "different-rules"}):
        changed = baseline.model_copy(update={
            "comparison": baseline.comparison.model_copy(update=update),
        })
        assert compare_quality_metrics(baseline, changed) == "NOT_COMPARABLE"


def test_frozen_java_pilot_quality_runs_on_a_verified_copy(analyze, quality_analyzer):
    analyzer, libraries = quality_analyzer
    original = ROOT / "experiments/original-ai-code/java-inventory-v0"
    files = {file.relative_to(original).as_posix(): file.read_bytes()
             for file in sorted(original.rglob("*.java"))}
    assert files
    result = analyze(files, analyzer, libraries)
    capabilities = [capability for capability in records(result, Capability)
                    if capability.capability == "quality"]
    assert capabilities and all(capability.status == "SUPPORTED" for capability in capabilities)
    assert all(metric.measurement == "MEASURED" for metric in records(result, Metric))
    for path, data in files.items():
        assert (original / path).read_bytes() == data


def test_missing_distribution_has_no_measured_zero(analyze, tmp_path):
    result = analyze({PREFIX + "Clean.java": b"package example; class Clean {}\n"},
                     QualityAnalyzer(tmp_path / "absent"))
    capability = next(cap for cap in records(result, Capability) if cap.capability == "quality")
    assert capability.status == "UNAVAILABLE" and not capability.evidence_ids
    assert all(metric.measurement == "UNAVAILABLE" and metric.value is None
               for metric in records(result, Metric))


def test_invalid_java_is_not_a_clean_quality_result(analyze, quality_analyzer):
    analyzer, libraries = quality_analyzer
    result = analyze({PREFIX + "Broken.java": b"package example; class Broken { # }\n"},
                     analyzer, libraries)
    quality = result.report["components"][0]["quality"]
    assert quality["pmd"]["status"] == "UNAVAILABLE"
    assert quality["pmd"]["artifact_id"]
    metric = next(item for item in records(result, Metric) if item.name == "pmd_finding_count")
    assert metric.measurement == "UNAVAILABLE" and metric.value is None


@pytest.mark.parametrize("bad_path", ("../Sample.java", "/Sample.java", "C:/Sample.java",
                                      "src/OutOfScope.java", "src/./Sample.java"))
def test_report_paths_fail_closed(bad_path):
    report = (
        f'<pmd version="{VERSION}"><file name="{bad_path}">'
        '<violation rule="UnusedLocalVariable" ruleset="Best Practices"/>'
        "</file></pmd>"
    ).encode()
    run = ToolRun("pmd", VERSION, "0" * 64, None, None, raw=report)
    with pytest.raises(InvalidQualityReport, match="outside the scanned manifest"):
        parse_report(run, {"src/Sample.java"})


def test_report_requires_verified_version():
    run = ToolRun("cpd", VERSION, "0" * 64, None, None,
                  raw=b'<pmd-cpd pmdVersion="0.0.0"/>')
    with pytest.raises(InvalidQualityReport, match="format or version"):
        parse_report(run, set())
