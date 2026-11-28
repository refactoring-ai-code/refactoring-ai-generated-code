"""Capability manifest (FR-011): one Capability record per CIR capability dimension.

Analysis support never implies build, test, coverage, quality, security or safe_patch
support. A capability is SUPPORTED only when this analysis actually executed it and
produced verified deterministic-tool evidence; everything else carries an explicit
status and reason. Confidence is an observed resolution ratio, not an invented value.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from backend.core.schemas.models import CAPABILITIES

# Why each dimension is outside F04-JAVA. Kept as data so reports and tests share it.
NOT_IN_F04 = {
    "quality": "quality measurement requires analyze_version and verified PMD/CPD execution",
    "build": "build requires the isolated sandbox (F06-SANDBOX #16); F04 never compiles uploads",
    "test": "test execution requires the isolated sandbox (F06-SANDBOX #16); not run by F04",
    "coverage": "coverage requires sandboxed test execution (F06-SANDBOX #16); not run by F04",
    "safe_patch": ("safe_patch needs patch generation and candidate validation (F10-PATCH #25, "
                   "F11-VALIDATE #26); symbol analysis does not imply safe patching"),
    "security": "security scanning is delivered by F07A-SCAN (#18); not claimed by F04-JAVA",
}


@dataclass(frozen=True)
class CapabilityState:
    """Observed state of one capability dimension for one language component."""

    status: str
    reason: str | None = None
    confidence: float | None = None
    confidence_reason: str | None = None
    limitations: tuple[str, ...] = ()

    def confidence_record(self) -> dict:
        if self.confidence is None:
            return {"value": None, "reason": self.confidence_reason or "not measured"}
        return {"value": self.confidence, "reason": None}


def ratio(numerator: int, denominator: int, what: str) -> tuple[float | None, str | None]:
    """Observed ratio, or null with a reason when there is nothing to measure."""
    if denominator == 0:
        return None, f"no {what} observed in this component"
    return round(numerator / denominator, 6), None


def not_implemented(capability: str, language: str) -> CapabilityState:
    reason = NOT_IN_F04.get(capability) or f"{language} has no runtime adapter yet"
    return CapabilityState(
        "NOT_IMPLEMENTED", reason, None,
        "capability not implemented; no confidence can be reported",
    )


def capability_records(
    *,
    record_base: Mapping,
    identifier: callable,
    language: str,
    component_id: str,
    adapter_id: str,
    states: Mapping[str, CapabilityState],
    tool: Mapping | None,
    toolchain: Sequence[Mapping],
    evidence_ids: Sequence[str],
    proofs: Mapping[str, tuple[Mapping, Sequence[Mapping], Sequence[str]]] | None = None,
) -> list[dict]:
    """Build nine Capability records plus their LanguageAdapterCapabilities declaration."""
    records = []
    for name in CAPABILITIES:
        state = states.get(name) or not_implemented(name, language)
        supported = state.status == "SUPPORTED"
        observed_tool, observed_chain, observed_evidence = (proofs or {}).get(
            name, (tool, toolchain, evidence_ids),
        )
        records.append({
            **record_base,
            "kind": "Capability",
            "id": identifier("capability", language, component_id, name),
            "language": language,
            "component_id": component_id,
            "capability": name,
            "status": state.status,
            "confidence": state.confidence_record(),
            "tool": dict(observed_tool) if supported and observed_tool else None,
            "toolchain": [dict(item) for item in observed_chain] if supported else [],
            "evidence_ids": list(observed_evidence) if supported else [],
            "limitations": list(state.limitations),
            "reason": None if supported else state.reason,
        })
    implemented = any(item["status"] == "SUPPORTED" for item in records)
    records.append({
        **record_base,
        "kind": "LanguageAdapterCapabilities",
        "id": identifier("adaptercaps", language, component_id),
        "adapter_id": adapter_id,
        "language": language,
        "component_id": component_id,
        "implementation_state": "RUNTIME_IMPLEMENTED" if implemented else "CONTRACT_DEFINED",
        "capability_ids": [item["id"] for item in records],
    })
    return records
