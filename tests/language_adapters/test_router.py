"""FR-008 routing: per file/component, hint-aware, never silently Java."""

from conftest import manifest_for

from backend.language_adapters.router import (
    ROUTED,
    UNKNOWN_LANGUAGE,
    UNSUPPORTED_LANGUAGE,
    component_identifier,
    route,
)

MIXED = {
    "service/pom.xml": b"<project/>",
    "service/src/main/java/a/Api.java": b"package a; class Api {}",
    "service/src/main/java/a/Impl.JAVA": b"package a; class Impl {}",
    "web/package.json": b"{}",
    "web/src/app.ts": b"export {}",
    "web/src/legacy.js": b"var x;",
    "tools/gen.py": b"print(1)",
    "native/lib.h": b"int f(void);",
    "native/lib.c": b"int f(void){return 0;}",
    "docs/readme.txt": b"java code inside a text file: class X {}",
    "scripts/Build.java.txt": b"class NotParsed {}",
    "Makefile": b"all:",
}


def by_path(plan):
    return {item.path: item for item in plan.files}


def test_mixed_project_routes_only_java_files_to_the_java_adapter():
    plan = route(manifest_for(MIXED), "java")
    files = by_path(plan)
    routed = {item.path for item in plan.files if item.status == ROUTED}
    assert routed == {"service/src/main/java/a/Api.java", "service/src/main/java/a/Impl.JAVA"}
    assert all(files[path].adapter_id == "adapter:java-javaparser" for path in routed)
    assert plan.mixed_language
    for path in ("web/src/app.ts", "web/src/legacy.js", "tools/gen.py", "native/lib.c"):
        assert files[path].status == UNSUPPORTED_LANGUAGE and files[path].adapter_id is None
        assert files[path].reason
    for path in ("docs/readme.txt", "scripts/Build.java.txt", "Makefile", "service/pom.xml",
                 "native/lib.h"):
        assert files[path].status == UNKNOWN_LANGUAGE, path
        assert files[path].language is None and "not parsed" in files[path].reason


def test_components_are_split_per_build_root_and_language():
    plan = route(manifest_for(MIXED))
    components = {(c.root, c.language): c for c in plan.components}
    java = components[("service", "JAVA")]
    assert java.build_systems == ("maven",) and java.adapter_id == "adapter:java-javaparser"
    assert set(java.paths) == {"service/src/main/java/a/Api.java",
                               "service/src/main/java/a/Impl.JAVA"}
    typescript, javascript = components[("web", "TYPESCRIPT")], components[("web", "JAVASCRIPT")]
    assert typescript.component_id != javascript.component_id
    assert components[("web", "TYPESCRIPT")].adapter_id is None
    assert components[("", "PYTHON")].paths == ("tools/gen.py",)
    assert java.component_id == component_identifier("service", "JAVA")


def test_user_hint_never_reroutes_a_detected_language():
    plan = route(manifest_for({"a/Main.java": b"class Main {}", "a/util.py": b"x = 1"}), "python")
    files = by_path(plan)
    assert files["a/Main.java"].status == ROUTED and files["a/Main.java"].language == "JAVA"
    assert files["a/util.py"].language == "PYTHON"
    assert plan.hint_mismatches == ("a/Main.java",)


def test_hint_only_disambiguates_an_unknown_header_and_does_not_parse_it():
    plan = route(manifest_for({"inc/api.h": b"int f(void);", "src/api.cpp": b"int f(){return 0;}"}),
                 "cpp")
    header = by_path(plan)["inc/api.h"]
    assert header.detected_language == "unknown" and header.hint_applied
    assert header.language == "CPP" and header.status == UNSUPPORTED_LANGUAGE
    assert "F14-CPP" in header.reason
    without_hint = by_path(route(manifest_for({"inc/api.h": b"int f(void);"})))["inc/api.h"]
    assert without_hint.status == UNKNOWN_LANGUAGE and not without_hint.hint_applied


def test_routing_is_deterministic_and_serialisable():
    manifest = manifest_for(MIXED)
    assert route(manifest, "java").as_dict() == route(manifest, "java").as_dict()
    assert route(manifest).as_dict()["files"][0]["path"] == "Makefile"
