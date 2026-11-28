"""Map genuine quality reports to CIR 1.0.0 and preserve each tool's evidence."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass
from xml.etree import ElementTree

from backend.analyzers.quality.runner import ToolRun
from backend.core.schemas.models import Metric
from backend.core.schemas.validation import canonical_sha256, metric_comparison_key
from backend.language_adapters.coordinates import (
    CoordinateError,
    SourceText,
    utf16_to_scalar_column,
)

PMD_RULES = {
    "CyclomaticComplexity": ("Design", "design", "COMPLEXITY"),
    "UnusedLocalVariable": ("Best Practices", "bestpractices", "QUALITY"),
    "EmptyCatchBlock": ("Error Prone", "errorprone", "QUALITY"),
    "ClassNamingConventions": ("Code Style", "codestyle", "QUALITY"),
}
CPD_RULE = "cpd/java/duplication"
UNKNOWN_LOCATION = "reported coordinates could not be verified against the snapshot"
VERIFIED = {"value": 1.0, "reason": None}


class InvalidQualityReport(ValueError):
    """An analyzer report cannot be tied to the expected tool and source scope."""


@dataclass(frozen=True, order=True)
class Position:
    path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def cir_range(self, source: SourceText) -> tuple[int, int, int, int]:
        start = utf16_to_scalar_column(source.line(self.start_line), self.start_column)
        end = utf16_to_scalar_column(source.line(self.end_line), self.end_column)
        if (self.end_line, end) <= (self.start_line, start):
            raise CoordinateError("quality range is empty or reversed")
        return self.start_line, start, self.end_line, end


@dataclass(frozen=True)
class Observation:
    rule: str
    category: str
    positions: tuple[Position, ...]
    tokens: int = 0
    lines: int = 0


@dataclass
class QualityRecords:
    records: list[dict]
    artifacts: list[dict]
    summaries: dict[str, dict]
    tool: dict
    toolchain: list[dict]
    evidence_ids: list[str]

    @property
    def supported(self) -> bool:
        return len(self.evidence_ids) == 2


def _path(raw: str, paths: set[str]) -> str:
    # The Windows renderer uses its native separators. The resulting path must
    # still match a case-sensitive manifest entry, with no cleanup or rebasing.
    path = raw.replace("\\", "/") if os.name == "nt" else raw
    if path not in paths or "\\" in path or ":" in path or any(
        part in ("", ".", "..") for part in path.split("/")
    ):
        raise InvalidQualityReport("quality report contains a path outside the scanned manifest")
    return path


def _name(element: ElementTree.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _position(element: ElementTree.Element, path: str, start: str, column: str) -> Position:
    def coordinate(key: str) -> int:
        try:
            return int(element.get(key, "0"))
        except ValueError:
            return 0

    return Position(path, coordinate(start), coordinate(column),
                    coordinate("endline"), coordinate("endcolumn"))


def parse_report(run: ToolRun, paths: set[str]) -> dict[tuple, Observation]:
    if run.raw is None or not run.version:
        raise InvalidQualityReport("no versioned quality report")
    root = ElementTree.fromstring(run.raw)
    pmd = run.tool_id == "pmd"
    if (_name(root) != ("pmd" if pmd else "pmd-cpd")
            or root.get("version" if pmd else "pmdVersion") != run.version):
        raise InvalidQualityReport("quality report format or version did not match")
    observations = {}
    for entry in root:
        kind = _name(entry)
        if kind in {"error", "configerror"}:
            raise InvalidQualityReport("quality report contains failed analysis entries")
        if pmd and kind == "file":
            path = _path(entry.get("name", ""), paths)
            for violation in entry:
                label, category, cir = PMD_RULES[violation.get("rule")]
                if _name(violation) != "violation" or violation.get("ruleset") != label:
                    raise InvalidQualityReport("PMD rule does not match the pinned ruleset")
                rule = f"pmd/java/{category}/{violation.get('rule')}"
                positions = (_position(violation, path, "beginline", "begincolumn"),)
                observations[rule, positions] = Observation(rule, cir, positions)
        elif not pmd and kind == "file":
            _path(entry.get("path", ""), paths)
        elif not pmd and kind == "duplication":
            positions = tuple(sorted({
                _position(child, _path(child.get("path", ""), paths), "line", "column")
                for child in entry if _name(child) == "file"
            }))
            tokens, lines = int(entry.get("tokens", "0")), int(entry.get("lines", "0"))
            if len(positions) < 2 or tokens < 1 or lines < 1:
                raise InvalidQualityReport("CPD group is missing occurrences or counts")
            observation = Observation(CPD_RULE, "DUPLICATION", positions, tokens, lines)
            key = (CPD_RULE, positions)
            if key in observations and observations[key] != observation:
                raise InvalidQualityReport("CPD reported conflicting counts for one group")
            observations[key] = observation
    return observations


def _location(base, identifier, position, file, data) -> dict:
    resolution, reason = "RESOLVED", None
    try:
        start_line, start, end_line, end = position.cir_range(SourceText.decode(data))
    except CoordinateError:
        resolution, reason = "UNRESOLVED", UNKNOWN_LOCATION
        start_line = start = end_line = end = None
    return {
        **base, "kind": "SourceLocation",
        "id": identifier("location", "quality", base["subject_sha256"], position),
        "path": file["path"], "file_id": file["id"], "file_sha256": file["sha256"],
        "resolution": resolution, "reason": reason, "symbol_id": None,
        "start_line": start_line, "start_column": start, "end_line": end_line, "end_column": end,
    }


def _evidence(base, evidence_id, run, artifact_id, rule, location_ids, resolved):
    return {
        **base, "kind": "Evidence", "id": evidence_id,
        "producer_kind": "DETERMINISTIC_TOOL", "actor_id": None, "tool": run.provenance(),
        "rule_id": rule, "model": None, "artifact_id": artifact_id,
        "location_ids": location_ids, "symbol_ids": [],
        "verification": "VERIFIED" if resolved else "UNCONFIRMED",
        "confidence": VERIFIED if resolved else {"value": None, "reason": UNKNOWN_LOCATION},
        "redaction": "UNREVIEWED",
    }


def _metric(base, identifier, run, component, paths, name, value, evidence_id, reason):
    comparison = {
        "tool": run.provenance(),
        "rule_set_version": "genesis-java-quality-v1" if run.tool_id == "pmd" else "cpd-java-v1",
        "rule_set_reason": None,
        "measurement_scope_sha256": canonical_sha256({
            "language": "JAVA", "paths": sorted(paths), "definition": name,
        }),
        "environment_sha256": run.environment_sha256,
        "environment_reason": None if run.environment_sha256 else "JVM fingerprint unavailable",
        "test_suite_sha256": None, "test_suite_state": "NOT_APPLICABLE",
    }
    record = {
        **base, "kind": "Metric",
        "id": identifier("metric", base["subject_sha256"], component, name),
        "name": name, "unit": "COUNT", "currency_code": None, "phase": "BASELINE",
        "value": value, "measurement": "MEASURED" if reason is None else "UNAVAILABLE",
        "reason": reason, "comparison": comparison, "direction": "LOWER_IS_BETTER",
        "population": "NONE", "denominator": None, "attempt_ids": [],
        "evidence_ids": [evidence_id] if evidence_id else [],
    }
    return {**record, "comparison_key": metric_comparison_key(record)}


def compare_quality_metrics(baseline: Metric, candidate: Metric) -> str:
    """Return the outcome for two measured, identical definitions and logical scopes."""
    if (baseline.measurement != "MEASURED" or candidate.measurement != "MEASURED"
            or metric_comparison_key(baseline) != metric_comparison_key(candidate)):
        return "NOT_COMPARABLE"
    if baseline.value == candidate.value:
        return "UNCHANGED"
    return "IMPROVED" if candidate.value < baseline.value else "WORSE"


def _correlate(findings: list[dict], locations: dict[str, dict], evidence: dict[str, dict]) -> None:
    """Associate overlapping independent observations while retaining their rule identities."""
    by_path = defaultdict(list)
    for finding in findings:
        if finding["eligibility"] != "ELIGIBLE":
            continue
        own_evidence = finding["evidence_ids"][0]
        for location_id in finding["location_ids"]:
            site = locations[location_id]
            by_path[site["path"]].append((
                (site["start_line"], site["start_column"]),
                (site["end_line"], site["end_column"]),
                finding["id"], own_evidence,
            ))
    related = defaultdict(set)
    for sites in by_path.values():
        active = []
        for start, end, finding_id, evidence_id in sorted(sites):
            active = [site for site in active if site[0] > start]
            tool_id = evidence[evidence_id]["tool"]["tool_id"]
            for _, other_finding, other_evidence in active:
                if evidence[other_evidence]["tool"]["tool_id"] != tool_id:
                    related[finding_id].add(other_evidence)
                    related[other_finding].add(evidence_id)
            active.append((end, finding_id, evidence_id))
    for finding in findings:
        finding["evidence_ids"].extend(sorted(related[finding["id"]]))


def normalize_quality(
    runs, *, base, identifier, component, paths, files, sources,
) -> QualityRecords:
    locations, evidence = {}, {}
    artifacts, findings, metrics = [], [], []
    summaries, successful_evidence = {}, []
    for run in runs:
        reason = run.reason
        observations = {}
        if reason is None:
            try:
                observations = parse_report(run, set(paths))
            except (ElementTree.ParseError, KeyError, ValueError):
                reason = "quality report could not be matched to the pinned rules and source paths"
        report_id = None
        if run.report_sha256:
            report_id = identifier("artifact", "quality-xml", run.report_sha256)
            artifacts.append({
                "id": report_id, "sha256": run.report_sha256,
                "media_type": "application/xml", "redaction": "UNREVIEWED",
            })
        summaries[run.tool_id] = {
            "status": "COMPLETED" if reason is None else "UNAVAILABLE",
            "reason": reason, "tool": run.provenance(), "artifact_id": report_id,
        }
        run_evidence = None
        if reason is None:
            run_evidence = identifier("evidence", base["subject_sha256"], component,
                                      run.tool_id, report_id)
            evidence[run_evidence] = _evidence(
                base, run_evidence, run, report_id, None, [], True,
            )
            successful_evidence.append(run_evidence)
            for observation in observations.values():
                site_ids = []
                for position in observation.positions:
                    site = _location(base, identifier, position, files[position.path],
                                     sources[position.path])
                    locations[site["id"]] = site
                    site_ids.append(site["id"])
                resolved = all(locations[site]["resolution"] == "RESOLVED" for site in site_ids)
                finding_id = identifier("finding", base["subject_sha256"], component, run.tool_id,
                                        observation.rule, *site_ids)
                proof_id = identifier("evidence", finding_id, report_id)
                evidence[proof_id] = _evidence(
                    base, proof_id, run, report_id, observation.rule, site_ids, resolved,
                )
                findings.append({
                    **base, "kind": "Finding", "id": finding_id,
                    "classification": "QUALITY_REFACTOR", "category": observation.category,
                    "rule_id": observation.rule, "tool": run.provenance(),
                    "location_ids": site_ids, "evidence_ids": [proof_id],
                    "confidence": evidence[proof_id]["confidence"],
                    "eligibility": "ELIGIBLE" if resolved else "UNRESOLVED",
                    "eligibility_reason": None if resolved else UNKNOWN_LOCATION,
                    "status": "OPEN" if resolved else "UNVERIFIED",
                })
        values = {"pmd_finding_count": len(observations)} if run.tool_id == "pmd" else {
            "cpd_duplicate_token_count": sum(item.tokens for item in observations.values()),
            "cpd_duplicate_line_count": sum(item.lines for item in observations.values()),
        }
        for name, value in values.items():
            metrics.append(_metric(base, identifier, run, component, paths, name,
                                   None if reason else value, run_evidence, reason))
    _correlate(findings, locations, evidence)
    toolchain = [{"name": run.tool_id, "version": run.version, "status": "AVAILABLE",
                  "reason": None} for run in runs if run.version]
    if runs[0].java_version:
        toolchain.append({"name": "java", "version": runs[0].java_version,
                          "status": "AVAILABLE", "reason": None})
    return QualityRecords([*locations.values(), *evidence.values(), *findings, *metrics], artifacts,
                          summaries, runs[0].provenance(), toolchain, successful_evidence)
