"""F04-JAVA entry point: immutable V0 -> routing plan -> Java symbols -> validated CIR bundle.

`analyze_version` reads a V0 snapshot through F03-INPUT `SourceSnapshots.workspace`, which
materialises a verified temporary copy and re-verifies V0 afterwards. `analyze_snapshot`
analyses an already materialised copy and first re-checks every file's SHA-256 against
the canonical manifest, so parsing never runs on bytes that differ from V0.

The result bundle is validated with the F02 `validate_bundle` closed-graph rules.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import rfc8785

from backend.core.schemas.models import ContractBundle, Scope
from backend.core.schemas.validation import ContractViolation, validate_bundle
from backend.language_adapters.capabilities import CapabilityState, capability_records, ratio
from backend.language_adapters.java.adapter import (
    ADAPTER_ID,
    DETERMINISTIC_CONFIDENCE,
    ComponentCounts,
    JavaRecordBuilder,
    JavaSymbolAdapter,
    evidence_tool,
    toolchain,
)
from backend.language_adapters.router import RoutingPlan, route


class SnapshotIntegrityError(RuntimeError):
    """The materialised copy differs from the immutable V0 manifest."""


@dataclass(frozen=True)
class AnalysisResult:
    plan: RoutingPlan
    bundle: ContractBundle | None
    report: dict


def _identifier(prefix: str, *parts) -> str:
    digest = hashlib.sha256("\0".join(str(part) for part in parts).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:40]}"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def read_verified_sources(root: Path, manifest: Mapping) -> dict[str, bytes]:
    """Read every manifest file from the copy and require its exact V0 SHA-256 and size."""
    sources: dict[str, bytes] = {}
    base = root.resolve()
    for item in manifest["files"]:
        target = base.joinpath(*item["path"].split("/"))
        if target.is_symlink() or not target.resolve().is_relative_to(base) or not target.is_file():
            raise SnapshotIntegrityError("materialised file is missing or not a regular file")
        data = target.read_bytes()
        if len(data) != item["size"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise SnapshotIntegrityError("materialised file differs from the V0 manifest")
        sources[item["path"]] = data
    return sources


def analyze_snapshot(root: Path, manifest: Mapping, manifest_sha256: str, scope: Scope, *,
                     selected_language: str | None = None, adapter: JavaSymbolAdapter | None = None,
                     recorded_at: str | None = None) -> AnalysisResult:
    if hashlib.sha256(rfc8785.dumps(dict(manifest))).hexdigest() != manifest_sha256:
        raise SnapshotIntegrityError("manifest bytes differ from the recorded manifest SHA-256")
    if scope.baseline_sha256 != manifest_sha256:
        raise ContractViolation("SCOPE_MISMATCH", "baseline_sha256")
    sources = read_verified_sources(root, manifest)
    plan = route(manifest, selected_language)
    adapter = adapter or JavaSymbolAdapter()
    base = {"schema_version": "1.0.0", "scope": scope.model_dump(mode="json"),
            "subject_sha256": manifest_sha256, "recorded_at": recorded_at or _utc_now()}
    files = {
        item["path"]: {"id": _identifier("file", manifest_sha256, item["path"]),
                       "path": item["path"], "sha256": item["sha256"],
                       "subject_sha256": manifest_sha256, "is_symlink": False,
                       "frozen": False, "protected_test": False}
        for item in manifest["files"]
    }
    manifest_artifact = {"id": _identifier("artifact", "v0-manifest", manifest_sha256),
                         "sha256": manifest_sha256, "media_type": "application/json",
                         "redaction": "UNREVIEWED"}
    artifacts = [manifest_artifact]
    records: list[dict] = []
    component_reports = []

    java_paths = [item.path for item in plan.for_language("JAVA")]
    run = adapter.run(root, java_paths) if java_paths else None
    builder = None
    if run is not None and run.status == "COMPLETED":
        output_sha256 = hashlib.sha256(run.raw).hexdigest()
        output_artifact = {"id": _identifier("artifact", "java-helper-output", output_sha256),
                           "sha256": output_sha256,
                           "media_type": "application/json", "redaction": "UNREVIEWED"}
        artifacts.append(output_artifact)
        builder = JavaRecordBuilder(base=base, identifier=_identifier,
                                    evidence_tool=evidence_tool(run.data),
                                    artifact_id=output_artifact["id"], files=files, sources=sources)
        builder.index_run(run.data)

    for component in plan.components:
        if component.language == "JAVA" and builder is not None:
            counts = ComponentCounts()
            builder.add_component(run.data, component.paths, counts)
            run_evidence = _identifier("evidence", "java-run", component.component_id)
            records.append({
                **base, "kind": "Evidence", "id": run_evidence,
                "producer_kind": "DETERMINISTIC_TOOL", "actor_id": None,
                "tool": evidence_tool(run.data), "rule_id": None, "model": None,
                "artifact_id": builder.artifact_id, "location_ids": [], "symbol_ids": [],
                "verification": "VERIFIED",
                "confidence": DETERMINISTIC_CONFIDENCE,
                "redaction": "UNREVIEWED",
            })
            states = _java_states(counts)
            records += capability_records(
                record_base=base, identifier=_identifier, language="JAVA",
                component_id=component.component_id, adapter_id=ADAPTER_ID, states=states,
                tool=evidence_tool(run.data), toolchain=toolchain(run.data),
                evidence_ids=[run_evidence])
            component_reports.append({**component.as_dict(), "run_status": run.status,
                                      "counts": counts.__dict__})
        else:
            states = {}
            reason = None
            if component.language == "JAVA":
                reason = (run.reason if run else None) or "Java analysis did not run"
                unavailable = CapabilityState("UNAVAILABLE", reason, None,
                                              "toolchain unavailable; nothing was measured")
                states = {"parse": unavailable, "symbol": unavailable, "dependency": unavailable}
            records += capability_records(
                record_base=base, identifier=_identifier, language=component.language,
                component_id=component.component_id,
                adapter_id=component.adapter_id or f"adapter:{component.language.lower()}-pending",
                states=states, tool=None, toolchain=[], evidence_ids=[])
            java_status = run.status if run and component.language == "JAVA" else "NOT_RUN"
            component_reports.append({**component.as_dict(), "run_status": java_status,
                                      "reason": reason})
    if builder is not None:
        records = builder.records + records

    payload = {"schema_version": "1.0.0", "mode": "INTERCHANGE",
               "scope": scope.model_dump(mode="json"), "files": list(files.values()),
               "artifacts": artifacts, "test_suites": [], "attempts": [], "records": records}
    # A snapshot without any recognised source language has no CIR record to report;
    # the routing report still lists every file and why it was not parsed.
    bundle = validate_bundle(payload) if records else None
    report = {
        "routing": plan.as_dict(),
        "java_run": {"status": run.status, "reason": run.reason,
                     "tool": run.data["tool"] if run.data else None,
                     "configuration": run.data["configuration"] if run.data else None,
                     "source_roots": run.data["source_roots"] if run.data else None}
        if run else {"status": "NOT_RUN", "reason": "no Java files were routed"},
        "components": component_reports,
        "files": builder.report if builder else [],
    }
    return AnalysisResult(plan, bundle, json.loads(json.dumps(report)))


def _java_states(counts: ComponentCounts) -> dict[str, CapabilityState]:
    parse_ratio, parse_reason = ratio(counts.parsed_files, counts.java_files, "Java files")
    symbol_ratio, symbol_reason = ratio(counts.resolved_declarations, counts.declarations,
                                        "declarations")
    edge_ratio, edge_reason = ratio(counts.resolved_references, counts.references, "references")
    return {
        "parse": CapabilityState(
            "SUPPORTED", confidence=parse_ratio, confidence_reason=parse_reason,
            limitations=("Java 21 language level; unicode escapes are not preprocessed",
                         "a file with syntax errors yields parse problems and no symbols")),
        "symbol": CapabilityState(
            "SUPPORTED", confidence=symbol_ratio, confidence_reason=symbol_reason,
            limitations=("types, methods, constructors and fields; local variables excluded",
                         "standalone-CR or invalid UTF-8 files produce unresolved locations")),
        "dependency": CapabilityState(
            "SUPPORTED", confidence=edge_ratio, confidence_reason=edge_reason,
            limitations=("CALL edges for method, constructor and this/super invocations only",
                         "JRE resolved by reflection; third-party libraries stay unresolved",
                         "ambiguous overloads stay UNRESOLVED with their candidate set")),
    }


def analyze_version(snapshots, actor_id: str, version_id: str, scope: Scope, *,
                    adapter: JavaSymbolAdapter | None = None,
                    recorded_at: str | None = None) -> AnalysisResult:
    """Analyse an owner's V0 through a verified F03 derivative copy."""
    if scope.version_id != version_id:
        raise ContractViolation("SCOPE_MISMATCH", "version_id")
    described = snapshots.describe(actor_id, version_id)
    if described["project_id"] != scope.project_id:
        raise ContractViolation("SCOPE_MISMATCH", "project_id")
    with snapshots.workspace(actor_id, version_id, "candidate") as derivative:
        if derivative.baseline_sha256 != described["manifest_sha256"]:
            raise SnapshotIntegrityError("derivative was not created from the described V0")
        return analyze_snapshot(
            derivative.path, described["manifest"], described["manifest_sha256"], scope,
            selected_language=described["selected_language"], adapter=adapter,
            recorded_at=recorded_at)
