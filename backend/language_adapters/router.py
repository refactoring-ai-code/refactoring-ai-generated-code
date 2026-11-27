"""Language Router (FR-008): route each V0 file and component to an adapter explicitly.

Input is the F03-INPUT canonical manifest (`files[].path`, `sha256`, `detected_language`)
and the user's optional `selected_language`. The user selection is a hint only. It can
disambiguate an extension F03 left as `unknown` (a `.h` header), but it never sends a
file to an adapter for another language. Every file receives an explicit route status:

* ``ROUTED``                - an implemented runtime adapter will analyse the file;
* ``UNSUPPORTED_LANGUAGE``  - the language is recognised but has no runtime adapter yet;
* ``UNKNOWN_LANGUAGE``      - the file is not recognised as source and is not parsed.

Components are (build root, language) pairs. A build root is the deepest directory that
contains a recognised build descriptor (``pom.xml``, ``package.json`` ...); files outside
any build root belong to the snapshot root. A mixed project yields one component per
language, so Java and the other languages are never analysed as one unit.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath

# F03-INPUT `detected_language` values -> CIR Language enumeration.
F03_TO_CIR = {
    "java": "JAVA",
    "python": "PYTHON",
    "javascript": "JAVASCRIPT",
    "typescript": "TYPESCRIPT",
    "csharp": "CSHARP",
    "go": "GO",
    "cpp": "CPP",
}
# Recognised source languages that are outside the CIR first-delivery enumeration.
NON_CIR_LANGUAGES = {"c": "C is outside the CIR 1.0.0 language enumeration"}
# User hints accepted for headers that F03 cannot classify by extension alone.
HEADER_HINTS = {"cpp": "cpp", "c++": "cpp", "c": "c"}
HEADER_SUFFIXES = {".h"}

# Implemented runtime adapters. Others are declared CONTRACT_DEFINED by the manifest.
RUNTIME_ADAPTERS = {"JAVA": "adapter:java-javaparser"}
PENDING_ADAPTER_TASKS = {
    "PYTHON": "F14-PY (#32)",
    "JAVASCRIPT": "F14-JSTS (#33)",
    "TYPESCRIPT": "F14-JSTS (#33)",
    "CSHARP": "F14-CS (#40)",
    "GO": "F14-GO (#41)",
    "CPP": "F14-CPP (#42)",
}

BUILD_DESCRIPTORS = {
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "settings.gradle": "gradle",
    "package.json": "npm",
    "tsconfig.json": "typescript",
    "pyproject.toml": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "go.work": "go",
    "CMakeLists.txt": "cmake",
    "compile_commands.json": "cmake",
}
BUILD_DESCRIPTOR_SUFFIXES = {".csproj": "dotnet", ".sln": "dotnet"}

ROUTED = "ROUTED"
UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
UNKNOWN_LANGUAGE = "UNKNOWN_LANGUAGE"


@dataclass(frozen=True)
class RoutedFile:
    path: str
    sha256: str
    detected_language: str
    language: str | None
    status: str
    adapter_id: str | None
    component_id: str | None
    component_root: str
    reason: str | None
    hint_applied: bool = False

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass(frozen=True)
class Component:
    component_id: str
    root: str
    language: str
    build_systems: tuple[str, ...]
    adapter_id: str | None
    paths: tuple[str, ...]

    def as_dict(self) -> dict:
        return {**self.__dict__, "build_systems": list(self.build_systems),
                "paths": list(self.paths)}


@dataclass(frozen=True)
class RoutingPlan:
    selected_language: str | None
    files: tuple[RoutedFile, ...]
    components: tuple[Component, ...]
    hint_mismatches: tuple[str, ...] = field(default=())

    def for_language(self, language: str) -> list[RoutedFile]:
        return [item for item in self.files if item.status == ROUTED and item.language == language]

    @property
    def mixed_language(self) -> bool:
        return len({item.language for item in self.files if item.language}) > 1

    def as_dict(self) -> dict:
        return {
            "selected_language": self.selected_language,
            "mixed_language": self.mixed_language,
            "hint_mismatches": list(self.hint_mismatches),
            "files": [item.as_dict() for item in self.files],
            "components": [item.as_dict() for item in self.components],
        }


def component_identifier(root: str, language: str) -> str:
    digest = hashlib.sha256(f"{root}\0{language}".encode()).hexdigest()[:20]
    return f"component:{language.lower()}-{digest}"


def _build_roots(paths: Iterable[str]) -> dict[str, list[str]]:
    roots: dict[str, list[str]] = {}
    for path in paths:
        pure = PurePosixPath(path)
        system = BUILD_DESCRIPTORS.get(pure.name) or BUILD_DESCRIPTOR_SUFFIXES.get(pure.suffix)
        if system:
            parent = str(pure.parent)
            roots.setdefault("" if parent == "." else parent, []).append(system)
    return roots


def _owning_root(path: str, roots: Mapping[str, list[str]]) -> str:
    parents = [str(parent) for parent in PurePosixPath(path).parents]
    for parent in parents:  # nearest first
        key = "" if parent == "." else parent
        if key in roots:
            return key
    return ""


def _normalise_hint(selected_language: str | None) -> str | None:
    if selected_language is None:
        return None
    hint = selected_language.strip().casefold()
    return hint or None


def route(manifest: Mapping, selected_language: str | None = None) -> RoutingPlan:
    """Route every manifest file. Never reads file content and never guesses a language."""
    entries = sorted(manifest["files"], key=lambda item: item["path"])
    hint = _normalise_hint(selected_language)
    hint_cir = F03_TO_CIR.get(hint) if hint else None
    roots = _build_roots(item["path"] for item in entries)
    routed: list[RoutedFile] = []
    mismatches: list[str] = []
    for item in entries:
        path, detected = item["path"], item["detected_language"]
        language_key, applied = detected, False
        if detected == "unknown" and PurePosixPath(path).suffix.casefold() in HEADER_SUFFIXES \
                and hint in HEADER_HINTS:
            language_key, applied = HEADER_HINTS[hint], True
        root = _owning_root(path, roots)
        cir = F03_TO_CIR.get(language_key)
        if cir and hint_cir and cir != hint_cir:
            mismatches.append(path)
        if cir is None:
            reason = NON_CIR_LANGUAGES.get(language_key)
            status = UNSUPPORTED_LANGUAGE if reason else UNKNOWN_LANGUAGE
            routed.append(RoutedFile(
                path, item["sha256"], detected, None, status, None, None, root,
                reason or "no recognised source-language extension; the file is not parsed",
                applied))
            continue
        adapter = RUNTIME_ADAPTERS.get(cir)
        reason = None
        if applied:
            reason = "header language taken from the user selection hint"
        if adapter is None:
            reason = (f"{cir} has no runtime adapter yet ({PENDING_ADAPTER_TASKS[cir]}); "
                      "the file is not parsed")
        routed.append(RoutedFile(
            path, item["sha256"], detected, cir, ROUTED if adapter else UNSUPPORTED_LANGUAGE,
            adapter, component_identifier(root, cir), root, reason, applied))
    components: dict[str, list[RoutedFile]] = {}
    for item in routed:
        if item.component_id:
            components.setdefault(item.component_id, []).append(item)
    return RoutingPlan(
        selected_language=selected_language,
        files=tuple(routed),
        components=tuple(
            Component(component_id, members[0].component_root, members[0].language,
                      tuple(sorted(set(roots.get(members[0].component_root, [])))),
                      RUNTIME_ADAPTERS.get(members[0].language),
                      tuple(member.path for member in members))
            for component_id, members in sorted(components.items())
        ),
        hint_mismatches=tuple(mismatches),
    )
