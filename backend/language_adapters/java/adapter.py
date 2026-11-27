"""Java symbol adapter (FR-010): JavaParser Symbol Solver output -> CIR records.

The Maven-built helper (``helper/``) parses and resolves source text only. It never
compiles, class-loads or executes analysed code; JRE types are resolved reflectively
and project types from the source tree. Third-party libraries are deliberately not
resolved, so a call into one remains UNRESOLVED with a MISSING_DEPENDENCY reason.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from backend.core.schemas.coordinates import source_offsets
from backend.core.schemas.models import SourceLocation
from backend.core.schemas.validation import ContractViolation, canonical_sha256
from backend.language_adapters.coordinates import (
    CoordinateError,
    SourceText,
    javaparser_range_to_cir,
    scalar_slice,
)

HELPER_DIR = Path(__file__).resolve().parent / "helper"
DEFAULT_JAR = HELPER_DIR / "target" / "java-symbol-helper.jar"
ADAPTER_ID = "adapter:java-javaparser"
MAX_TEXT = 2000
DETERMINISTIC_CONFIDENCE = {
    "value": None, "reason": "deterministic parser output; no probabilistic confidence"}


def _text(value: str) -> str:
    return value if len(value) <= MAX_TEXT else value[: MAX_TEXT - 3] + "..."


def build_helper(maven: str | None = None, timeout: int = 900) -> Path:
    """Explicit developer/CI step: build the pinned helper jar with Maven."""
    executable = maven or shutil.which("mvn") or shutil.which("mvn.cmd")
    if executable is None:
        raise RuntimeError("Maven executable not found")
    subprocess.run(
        [executable, "-B", "-q", "-DskipTests", "package"],
        cwd=HELPER_DIR, check=True, timeout=timeout,
    )
    if not DEFAULT_JAR.is_file():
        raise RuntimeError("Maven completed without producing the helper jar")
    return DEFAULT_JAR


@dataclass
class JavaRun:
    """Outcome of one helper execution over a source root."""

    status: str  # COMPLETED | UNAVAILABLE | FAILED
    reason: str | None = None
    raw: bytes | None = None
    data: dict | None = None
    requested: tuple[str, ...] = ()


@dataclass
class JavaSymbolAdapter:
    helper_jar: Path | None = None
    java: str | None = None
    timeout_seconds: int = 300
    max_heap: str = "768m"

    def jar(self) -> Path:
        configured = os.environ.get("GENESIS_JAVA_HELPER_JAR")
        return Path(self.helper_jar or configured or DEFAULT_JAR)

    def java_executable(self) -> str | None:
        if self.java:
            return self.java
        home = os.environ.get("JAVA_HOME")
        if home:
            for name in ("java", "java.exe"):
                candidate = Path(home) / "bin" / name
                if candidate.is_file():
                    return str(candidate)
        return shutil.which("java")

    def run(self, root: Path, paths: Sequence[str]) -> JavaRun:
        requested = tuple(paths)
        java, jar = self.java_executable(), self.jar()
        if java is None:
            return JavaRun("UNAVAILABLE", "Java runtime not found on PATH or JAVA_HOME",
                           requested=requested)
        if not jar.is_file():
            return JavaRun("UNAVAILABLE", "java-symbol-helper jar is not built (run build_helper)",
                           requested=requested)
        # Minimal environment: the helper needs no credentials, proxies or network.
        env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "JAVA_HOME", "TEMP", "TMP")
               if key in os.environ}
        command = [java, f"-Xmx{self.max_heap}", "-Xss8m", "-Duser.language=en",
                   "-Duser.country=US", "-Dfile.encoding=UTF-8", "-jar", str(jar), str(root)]
        try:
            completed = subprocess.run(
                command, input=("\n".join(requested) + "\n").encode("utf-8"),
                capture_output=True, timeout=self.timeout_seconds, env=env, check=False,
            )
        except subprocess.TimeoutExpired:
            return JavaRun("FAILED", f"helper exceeded {self.timeout_seconds} s",
                           requested=requested)
        except OSError as error:
            return JavaRun("UNAVAILABLE", f"helper could not start: {type(error).__name__}",
                           requested=requested)
        if completed.returncode != 0:
            return JavaRun("FAILED", f"helper exited with code {completed.returncode}",
                           requested=requested)
        try:
            data = json.loads(completed.stdout.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JavaRun("FAILED", "helper output is not valid UTF-8 JSON", requested=requested)
        if [item.get("path") for item in data.get("files", [])] != list(requested):
            return JavaRun("FAILED", "helper output does not match the requested files",
                           requested=requested)
        return JavaRun("COMPLETED", None, completed.stdout, data, requested)


def _parameter_count(signature: str) -> int | None:
    """Count top-level parameters in `a.b.C.m(T1, java.util.Map<K, V>)`; None if unknown."""
    match = re.search(r"\((.*)\)\s*$", signature or "")
    if not match:
        return None
    inner, depth, count = match.group(1).strip(), 0, 1
    if not inner:
        return 0
    for character in inner:
        depth += character == "<"
        depth -= character == ">"
        count += character == "," and depth == 0
    return count


@dataclass
class ComponentCounts:
    java_files: int = 0
    parsed_files: int = 0
    declarations: int = 0
    resolved_declarations: int = 0
    references: int = 0
    resolved_references: int = 0
    unresolved_by_status: dict[str, int] = field(default_factory=dict)


class JavaRecordBuilder:
    """Translate helper JSON into CIR records bound to the V0 file identities."""

    def __init__(self, *, base: Mapping, identifier: Callable[..., str], evidence_tool: Mapping,
                 artifact_id: str, files: Mapping[str, Mapping], sources: Mapping[str, bytes]):
        self.base = base
        self.identifier = identifier
        self.tool = evidence_tool
        self.artifact_id = artifact_id
        self.files = files  # path -> FileIdentity dict
        self.sources = sources  # path -> exact V0 bytes
        self.records: list[dict] = []
        self.external: dict[str, str] = {}
        self.report: list[dict] = []

    # -- locations -------------------------------------------------------------------
    def _unresolved_location(self, key: tuple, reason: str) -> dict:
        record = {
            **self.base, "kind": "SourceLocation", "id": self.identifier("location", *key),
            "path": None, "file_id": None, "file_sha256": None, "resolution": "UNRESOLVED",
            "reason": _text(reason), "start_line": None, "start_column": None,
            "end_line": None, "end_column": None, "symbol_id": None,
        }
        self.records.append(record)
        return record

    def _location(self, path: str, text: SourceText | None, text_error: str | None,
                  native, key: tuple, *, expect: tuple[list, str] | None = None) -> dict:
        reason = text_error
        coordinates = None
        if reason is None:
            try:
                coordinates = javaparser_range_to_cir(text, native)
                if expect is not None:
                    name_range, name = expect
                    if name_range is None or scalar_slice(
                            text, *javaparser_range_to_cir(text, name_range)) != name:
                        raise CoordinateError("converted name range does not cover the name")
            except CoordinateError as error:
                reason = f"coordinate conversion failed: {error}"
        if reason is not None:
            return self._unresolved_location(key, reason)
        identity = self.files[path]
        record = {
            **self.base, "kind": "SourceLocation", "id": self.identifier("location", *key),
            "path": path, "file_id": identity["id"], "file_sha256": identity["sha256"],
            "resolution": "RESOLVED", "reason": None,
            "start_line": coordinates[0], "start_column": coordinates[1],
            "end_line": coordinates[2], "end_column": coordinates[3], "symbol_id": None,
        }
        try:  # independent bound check with the F02 contract helper on the exact bytes
            source_offsets(SourceLocation.model_validate(record), self.sources[path])
        except (ContractViolation, ValueError):
            return self._unresolved_location(key, "converted range failed the source-byte check")
        self.records.append(record)
        return record

    # -- symbols -----------------------------------------------------------------------
    def _external_symbol(self, signature: str, origin: str, evidence_id: str) -> str:
        if signature in self.external:
            return self.external[signature]
        reason = ("implicit compiler-generated member; it has no source range"
                  if origin == "IMPLICIT" else
                  "declared outside the analysed snapshot (JDK or library); no source range")
        location = self._unresolved_location(("external", signature), reason)
        symbol_id = self.identifier("symbol", "external", signature)
        name = signature.split("(")[0].rsplit(".", 1)[-1] or signature
        self.records.append({
            **self.base, "kind": "Symbol", "id": symbol_id, "language": "JAVA",
            "name": _text(name), "signature": _text(signature), "location_id": location["id"],
            "resolution": "UNRESOLVED", "reason": reason, "public_api": None,
            "evidence_ids": [evidence_id],
        })
        self.external[signature] = symbol_id
        return symbol_id

    def add_file(self, entry: Mapping, counts: ComponentCounts) -> None:
        path = entry["path"]
        counts.java_files += 1
        text, text_error = None, None
        try:
            text = SourceText.decode(self.sources[path])
        except CoordinateError as error:
            text_error = f"source text cannot be mapped to CIR coordinates: {error}"
        evidence_id = self.identifier("evidence", "java-file", path)
        file_report = {"path": path, "status": entry["status"], "reason": entry.get("reason"),
                       "problems": [], "declarations": 0, "references": 0,
                       "unresolved_references": []}
        self.report.append(file_report)
        for problem in entry.get("problems", []):
            converted = None
            if text is not None and problem.get("range"):
                try:
                    converted = list(javaparser_range_to_cir(text, problem["range"]))
                except CoordinateError:
                    converted = None
            file_report["problems"].append({"message": problem.get("message"), "range": converted})
        if entry["status"] != "PARSED":
            return
        counts.parsed_files += 1
        location_ids, symbol_ids = [], []
        for index, declaration in enumerate(entry["declarations"]):
            counts.declarations += 1
            key = ("declaration", path, index, declaration["kind"], declaration["signature"])
            location = self._location(path, text, text_error, declaration["range"], key,
                                      expect=(declaration["name_range"], declaration["name"]))
            symbol_id = self.identifier("symbol", *key)
            resolved = declaration["resolved"] and location["resolution"] == "RESOLVED"
            reason = None
            if not declaration["resolved"]:
                reason = declaration["reason"] or "declaration signature could not be resolved"
            elif location["resolution"] != "RESOLVED":
                reason = location["reason"]
            counts.resolved_declarations += resolved
            self.records.append({
                **self.base, "kind": "Symbol", "id": symbol_id, "language": "JAVA",
                "name": _text(declaration["name"]),
                "signature": _text(declaration["signature"]) if declaration["signature"] else None,
                "location_id": location["id"],
                "resolution": "RESOLVED" if resolved else "UNRESOLVED",
                "reason": _text(reason) if reason else None,
                "public_api": declaration["public_api"], "evidence_ids": [evidence_id],
            })
            location["symbol_id"] = symbol_id
            location_ids.append(location["id"])
            symbol_ids.append(symbol_id)
        file_report["declarations"] = len(entry["declarations"])
        for index, reference in enumerate(entry["references"]):
            counts.references += 1
            key = ("reference", path, index, reference["kind"], reference["name"])
            location = self._location(path, text, text_error,
                                      reference["name_range"] or reference["range"], key)
            location_ids.append(location["id"])
            target_id, reason = None, None
            status = reference["status"]
            if status == "RESOLVED":
                origin, target = reference["target_origin"], reference["target"]
                if origin == "SOURCE":
                    matches = self.signatures.get(target, [])
                    if len(matches) == 1:
                        target_id = matches[0]
                    else:
                        reason = ("DUPLICATE_DECLARATION: resolved signature matches "
                                  f"{len(matches)} analysed declarations" if matches else
                                  "resolved declaration is not among the analysed symbols")
                else:
                    target_id = self._external_symbol(target, origin, evidence_id)
            else:
                reason = f"{status}: {reference['reason'] or 'reference could not be resolved'}"
                if status == "AMBIGUOUS":
                    arity = reference.get("argument_count")
                    candidates = sorted({
                        signature for signature in self.same_name.get(reference["name"], [])
                        if arity is None or _parameter_count(signature) in (arity, None)
                        or "..." in signature})
                    if candidates:
                        reason += "; same-name declarations in analysed sources: " + "; ".join(
                            candidates)
            if target_id is not None:
                counts.resolved_references += 1
                location["symbol_id"] = target_id
            else:
                counts.unresolved_by_status[status if status != "RESOLVED" else "UNLINKED"] = (
                    counts.unresolved_by_status.get(
                        status if status != "RESOLVED" else "UNLINKED", 0) + 1)
                file_report["unresolved_references"].append(
                    {"name": reference["name"], "status": status, "reason": reason,
                     "location_id": location["id"]})
            source_matches = self.signatures.get(reference["from"], []) if reference["from"] else []
            if len(source_matches) != 1:
                continue  # no single enclosing declaration; the call-site location remains
            self.records.append({
                **self.base, "kind": "DependencyEdge",
                "id": self.identifier("dependency", *key),
                "from_symbol_id": source_matches[0], "to_symbol_id": target_id,
                "relationship": "CALL",
                "resolution": "RESOLVED" if target_id else "UNRESOLVED",
                "reason": None if target_id else _text(reason), "evidence_ids": [evidence_id],
            })
        file_report["references"] = len(entry["references"])
        self.records.append({
            **self.base, "kind": "Evidence", "id": evidence_id,
            "producer_kind": "DETERMINISTIC_TOOL",
            "actor_id": None, "tool": dict(self.tool), "rule_id": None, "model": None,
            "artifact_id": self.artifact_id, "location_ids": location_ids,
            "symbol_ids": symbol_ids, "verification": "VERIFIED",
            "confidence": DETERMINISTIC_CONFIDENCE, "redaction": "UNREVIEWED",
        })

    def index_run(self, data: Mapping) -> None:
        """Index declarations of every analysed file so cross-file and cross-component
        calls link to the exact overload declared in source."""
        self.signatures: dict[str, list[str]] = {}
        self.same_name: dict[str, list[str]] = {}
        for entry in data["files"]:
            for index, declaration in enumerate(entry.get("declarations", [])):
                if declaration["signature"]:
                    key = ("declaration", entry["path"], index, declaration["kind"],
                           declaration["signature"])
                    self.signatures.setdefault(declaration["signature"], []).append(
                        self.identifier("symbol", *key))
                    if declaration["kind"] in ("METHOD", "CONSTRUCTOR"):
                        self.same_name.setdefault(declaration["name"], []).append(
                            declaration["signature"])

    def add_component(self, data: Mapping, paths: Sequence[str], counts: ComponentCounts) -> None:
        wanted = set(paths)
        for entry in data["files"]:
            if entry["path"] in wanted:
                self.add_file(entry, counts)


def evidence_tool(data: Mapping) -> dict:
    tool = data["tool"]
    return {
        "tool_id": "javaparser-symbol-solver-core/java-symbol-helper",
        "version": f"{tool['parser_version']}+helper-{tool['helper_version']}",
        "version_reason": None,
        "config_sha256": canonical_sha256(dict(data["configuration"])),
        "config_reason": None,
    }


def toolchain(data: Mapping) -> list[dict]:
    tool = data["tool"]
    return [
        {"name": "java", "version": f"{tool['java_version']} ({tool['java_vendor']})",
         "status": "AVAILABLE", "reason": None},
        {"name": "javaparser-symbol-solver-core", "version": tool["parser_version"],
         "status": "AVAILABLE", "reason": None},
        {"name": "java-symbol-helper", "version": tool["helper_version"],
         "status": "AVAILABLE", "reason": None},
    ]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
