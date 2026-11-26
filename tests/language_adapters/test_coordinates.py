"""Coordinate conversion: JavaParser UTF-16 inclusive -> CIR scalar exclusive -> Monaco."""

import json
import shutil
import subprocess

import pytest
from conftest import ROOT

from backend.language_adapters.coordinates import (
    CoordinateError,
    SourceText,
    inclusive_utf16_end_to_scalar_end,
    javaparser_range_to_cir,
    monaco_range,
    scalar_slice,
    utf16_to_scalar_column,
)

ASTRAL = "\U0001F600"  # one scalar, two UTF-16 units


def utf16_column(line: str, scalar_column: int) -> int:
    """Independent reference implementation via the UTF-16 codec."""
    return len(line[: scalar_column - 1].encode("utf-16-le")) // 2 + 1


def test_astral_characters_shift_utf16_but_not_scalar_columns():
    line = f'\tx = "{ASTRAL}"; call();'
    native_start = line.index("call") + 1 + 1  # one extra UTF-16 unit before it
    assert utf16_to_scalar_column(line, native_start) == line.index("call") + 1
    with pytest.raises(CoordinateError):
        utf16_to_scalar_column(line, line.index(ASTRAL) + 2)  # inside the surrogate pair


def test_inclusive_end_covering_an_astral_character_includes_the_whole_character():
    line = f"a{ASTRAL}b"
    assert inclusive_utf16_end_to_scalar_end(line, 3) == 3  # low unit of the emoji
    assert inclusive_utf16_end_to_scalar_end(line, 2) == 3  # high unit -> whole scalar
    assert inclusive_utf16_end_to_scalar_end(line, 4) == 4


def test_tabs_count_one_column_and_crlf_is_one_line_break():
    source = SourceText.decode(b"class A {\r\n\t\tvoid m() {}\r\n}\r\n")
    assert source.lines[1] == "\t\tvoid m() {}"
    start_line, start, end_line, end = javaparser_range_to_cir(source, [2, 3, 2, 13])
    assert (start_line, start, end_line, end) == (2, 3, 2, 14)
    assert scalar_slice(source, start_line, start, end_line, end) == "void m() {}"


def test_multiline_ranges_and_exclusive_end():
    source = SourceText.decode(b"class B {\n  int x;\n}")
    rng = javaparser_range_to_cir(source, [1, 1, 3, 1])
    assert rng == (1, 1, 3, 2)
    assert scalar_slice(source, *rng) == "class B {\n  int x;\n}"


@pytest.mark.parametrize("data", [b"class A {}\rclass B {}", b"\xff\xfe broken"])
def test_standalone_cr_and_invalid_utf8_are_not_guessed(data):
    with pytest.raises(CoordinateError):
        SourceText.decode(data)


def test_out_of_range_and_reversed_ranges_are_rejected():
    source = SourceText.decode(b"ab\ncd")
    for native in ([3, 1, 3, 1], [1, 9, 1, 9], [2, 2, 1, 1], None):
        with pytest.raises(CoordinateError):
            javaparser_range_to_cir(source, native)


def test_monaco_mirror_matches_utf16_reference_implementation():
    text = f'\ts = "{ASTRAL}{ASTRAL}"; area(1);\r\nnext {ASTRAL}x'
    source = SourceText.decode(text.encode())
    line = source.lines[0]
    start = line.index("area") + 1
    result = monaco_range(source, 1, start, 2, 8)
    assert result == {"startLineNumber": 1, "startColumn": utf16_column(line, start),
                      "endLineNumber": 2, "endColumn": utf16_column(source.lines[1], 8)}
    assert result["startColumn"] == start + 2  # two astral characters before the call


def _node_supports_typescript():
    node = shutil.which("node")
    if node is None:
        return None
    probe = subprocess.run([node, "-e", "process.stdout.write(process.versions.node)"],
                           capture_output=True, text=True, check=False)
    major, minor = (int(part) for part in probe.stdout.split(".")[:2])
    return node if (major, minor) >= (22, 18) else None


def test_monaco_boundary_matches_the_frontend_sourceRange_implementation(tmp_path):
    """Run frontend/src/coordinates.ts itself (Node type stripping) on CRLF/tab/astral text."""
    node = _node_supports_typescript()
    if node is None:
        pytest.skip("Node.js >= 22.18 with TypeScript type stripping is not available")
    text = f'package p;\r\n\tclass {ASTRAL} {{}}\r\n\tvoid m() {{ f("{ASTRAL}"); g(); }}\r\n'
    source = SourceText.decode(text.encode())
    cases = [(2, 2, 2, 7), (3, 2, 3, 7), (3, 18, 3, 19), (1, 1, 3, 2)]
    module = (ROOT / "frontend" / "src" / "coordinates.ts").as_uri()
    script = tmp_path / "probe.mjs"
    script.write_text(
        f"import {{ sourceRange }} from {json.dumps(module)};\n"
        "const [text, cases] = JSON.parse(process.argv[2]);\n"
        "console.log(JSON.stringify(cases.map(c => sourceRange(text, ...c))));\n",
        encoding="utf-8")
    completed = subprocess.run([node, str(script), json.dumps([text, cases])],
                               capture_output=True, text=True, check=True, encoding="utf-8")
    frontend = json.loads(completed.stdout)
    assert frontend == [monaco_range(source, *case) for case in cases]
