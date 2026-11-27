"""Shared F04-JAVA fixtures: real F03 manifests, CIR scopes and the Maven-built helper."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import pytest
import rfc8785

from backend.core.schemas.models import Scope
from backend.language_adapters.java.adapter import DEFAULT_JAR, JavaSymbolAdapter, build_helper
from backend.storage.input_validation import SourceFile

ROOT = Path(__file__).resolve().parents[2]


def manifest_for(files: dict[str, bytes]) -> dict:
    """Build the F03 canonical manifest with F03's own extension-based detection."""
    records = []
    for path in sorted(files):
        data = files[path]
        language = SourceFile(path, data).language
        records.append({"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                        "detected_language": language, "is_source": language != "unknown",
                        "access_mode": "owner"})
    return {"schema_version": "1.0", "files": records, "excluded": []}


def manifest_sha256(manifest: dict) -> str:
    return hashlib.sha256(rfc8785.dumps(manifest)).hexdigest()


def scope_for(digest: str, version: str = "version:f04-test") -> Scope:
    return Scope(project_id="project:f04-test", version_id=version,
                 analysis_id="analysis:f04-test", run_id="run:f04-test",
                 source_revision="0" * 40, baseline_sha256=digest)


def materialise(root: Path, files: dict[str, bytes]) -> Path:
    for path, data in files.items():
        target = root.joinpath(*path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return root


@pytest.fixture(scope="session")
def helper_jar() -> Path:
    """The real helper. Missing Java/Maven is a failure, never a silent skip."""
    configured = os.environ.get("GENESIS_JAVA_HELPER_JAR")
    jar = Path(configured) if configured else DEFAULT_JAR
    if shutil.which("java") is None and not os.environ.get("JAVA_HOME"):
        pytest.fail("Java 21 runtime is required for F04-JAVA adapter tests")
    if not jar.is_file():
        jar = build_helper()
    return jar


@pytest.fixture
def java_adapter(helper_jar) -> JavaSymbolAdapter:
    return JavaSymbolAdapter(helper_jar=helper_jar)


@pytest.fixture
def snapshot(tmp_path):
    """Create a materialised V0 copy and return (root, manifest, digest, scope)."""

    def make(files: dict[str, bytes]):
        root = materialise(tmp_path / "v0", files)
        manifest = manifest_for(files)
        digest = manifest_sha256(manifest)
        return root, manifest, digest, scope_for(digest)

    return make
