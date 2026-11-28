"""Run PMD and CPD on the manifest-selected Java files without loading uploaded code."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from backend.analyzers.quality.distribution import CACHE, VERSION, installed_libraries
from backend.core.schemas.validation import canonical_sha256

RULESET = Path(__file__).resolve().with_name("ruleset.xml")
CPD_SOURCE = RULESET.with_name("CpdXml.java")
CPD_MIN_TOKENS = 50
MAX_REPORT_BYTES = 16 * 1024 * 1024
JVM_OPTIONS = ("-Duser.language=en", "-Duser.country=US", "-Duser.timezone=UTC",
               "-Dfile.encoding=UTF-8")
CLI_CLASS = "net.sourceforge.pmd.cli.PmdCli"


@dataclass(frozen=True)
class ToolRun:
    tool_id: str
    version: str | None
    config_sha256: str
    environment_sha256: str | None
    java_version: str | None
    report_sha256: str | None = None
    raw: bytes | None = None
    reason: str | None = None

    def provenance(self) -> dict:
        return {
            "tool_id": self.tool_id, "version": self.version,
            "version_reason": None if self.version else "pinned CLI version not verified",
            "config_sha256": self.config_sha256, "config_reason": None,
        }


def _java_executable() -> Path | None:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
        if candidate.is_file():
            return candidate.resolve()
    java = shutil.which("java")
    return Path(java).resolve() if java else None


def _environment() -> dict[str, str]:
    return {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TMP", "TEMP")
            if key in os.environ}


class QualityAnalyzer:
    """Read-only analyzer with a separate local cache for restricted raw report bytes."""

    def __init__(self, cache: Path = CACHE):
        self.cache = cache.resolve()

    def run(self, root: Path, paths: tuple[str, ...]) -> tuple[ToolRun, ToolRun]:
        pmd_config = hashlib.sha256(RULESET.read_bytes()).hexdigest()
        cpd_config = canonical_sha256({
            "language": "java-21", "minimum_tokens": CPD_MIN_TOKENS,
            "matching": "default", "encoding": "UTF-8", "report_format": "xml",
            "renderer_sha256": hashlib.sha256(CPD_SOURCE.read_bytes()).hexdigest(),
        })
        tools = (
            ("pmd", pmd_config, ("check", "--rulesets", str(RULESET), "--no-cache",
                                 "--use-version", "java-21")),
            ("cpd", cpd_config, ()),
        )
        java = _java_executable()
        libraries = installed_libraries(self.cache)
        if java is None or libraries is None:
            reason = "Java unavailable" if java is None else "pinned PMD is not installed"
            return tuple(ToolRun(tool, None, config, None, None, reason=reason)
                         for tool, config, _ in tools)

        env = _environment()
        jvm = [str(java), *JVM_OPTIONS, "-cp", str(libraries / "*")]
        launcher = [*jvm, CLI_CLASS]
        try:
            runtime = subprocess.run(
                [str(java), *JVM_OPTIONS, "-XshowSettings:properties", "-version"],
                cwd=libraries, env=env, capture_output=True, check=True, timeout=20,
            )
            runtime_properties = dict(re.findall(
                r"^\s*(java\.runtime\.version|java\.vendor|os\.arch|os\.name)\s*=\s*(.+?)\s*$",
                runtime.stderr.decode("utf-8", errors="replace"), re.MULTILINE,
            ))
            java_version = runtime_properties["java.runtime.version"]
            environment = canonical_sha256({
                "jvm": runtime_properties, "options": list(JVM_OPTIONS),
            })
            version = subprocess.run(
                [*launcher, "--version"], cwd=libraries, env=env,
                capture_output=True, check=True, timeout=20,
            )
            if not re.search(rb"\bPMD\s+" + re.escape(VERSION.encode()) + rb"\b",
                             version.stdout + version.stderr):
                raise ValueError("unexpected CLI version")
        except (OSError, subprocess.SubprocessError, KeyError, ValueError):
            return tuple(ToolRun(tool, None, config, None, None,
                                 reason="pinned PMD or Java runtime could not be verified")
                         for tool, config, _ in tools)

        with tempfile.TemporaryDirectory(prefix="genesis-quality-") as directory:
            work = Path(directory)
            file_list = work / "sources.txt"
            file_list.write_text("\n".join(paths) + "\n", encoding="utf-8", newline="\n")
            results = []
            for tool, config, command in tools:
                report = work / f"{tool}.xml"
                if tool == "pmd":
                    arguments = [
                        *launcher, *command, "--file-list", str(file_list),
                        "--relativize-paths-with", str(root.resolve()),
                        "--encoding", "UTF-8", "--format", "xml", "--report-file", str(report),
                    ]
                else:
                    arguments = [*jvm, str(CPD_SOURCE), str(file_list), str(report),
                                 str(CPD_MIN_TOKENS)]
                results.append(self._run_tool(tool, config, environment, java_version,
                                              arguments, root, env, report))
        return results[0], results[1]

    def _run_tool(self, tool, config, environment, java_version, arguments, root, env, report):
        try:
            execution = subprocess.run(arguments, cwd=root, env=env, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL, check=False, timeout=120)
            if not report.is_file() or report.stat().st_size > MAX_REPORT_BYTES:
                return ToolRun(tool, VERSION, config, environment, java_version,
                               reason="quality analyzer did not produce a bounded XML report")
            raw = report.read_bytes()
            report_hash = hashlib.sha256(raw).hexdigest()
            self._save_report(report_hash, raw)
        except subprocess.TimeoutExpired:
            return ToolRun(tool, VERSION, config, environment, java_version,
                           reason="quality analysis exceeded its time limit")
        except OSError:
            return ToolRun(tool, VERSION, config, environment, java_version,
                           reason="quality tool execution or evidence storage failed")
        # PMD/CPD use 4 for findings and 5 for an incomplete scan with recoverable errors.
        reason = None if execution.returncode in (0, 4) else "quality analysis did not complete"
        return ToolRun(tool, VERSION, config, environment, java_version, report_hash, raw, reason)

    def _save_report(self, digest: str, raw: bytes) -> None:
        reports = self.cache / "reports"
        reports.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=reports) as workspace:
            staged = Path(workspace) / "report.xml"
            with os.fdopen(os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                           "wb") as output:
                output.write(raw)
            staged.replace(reports / f"{digest}.xml")
