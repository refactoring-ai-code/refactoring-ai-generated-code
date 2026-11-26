"""Explicit coordinate conversion at the adapter boundary.

CIR locations use 1-based lines, 1-based Unicode-scalar columns and an exclusive end
(docs/contracts/SEMANTICS.md). JavaParser reports 1-based UTF-16 columns (tab size 1)
with an inclusive end. Monaco uses 1-based UTF-16 columns with an exclusive end. Every
conversion is computed from the actual decoded source text; nothing is guessed. Input
that cannot be mapped without guessing (standalone CR, invalid UTF-8, a column inside
a surrogate pair) raises CoordinateError so the caller records an unresolved location.
"""

from __future__ import annotations

from dataclasses import dataclass


class CoordinateError(ValueError):
    """The native position cannot be mapped to CIR coordinates without guessing."""


@dataclass(frozen=True)
class SourceText:
    """UTF-8 source decoded strictly, split into CIR logical lines (LF or CRLF)."""

    text: str
    lines: tuple[str, ...]

    @classmethod
    def decode(cls, data: bytes) -> SourceText:
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            raise CoordinateError("source is not valid UTF-8") from None
        raw = text.split("\n")
        lines = tuple(
            line[:-1] if index < len(raw) - 1 and line.endswith("\r") else line
            for index, line in enumerate(raw)
        )
        if any("\r" in line for line in lines):
            raise CoordinateError("standalone CR line terminator has no CIR line mapping")
        return cls(text, lines)

    def line(self, number: int) -> str:
        if not 1 <= number <= len(self.lines):
            raise CoordinateError("line is outside the source")
        return self.lines[number - 1]


def _utf16_units(character: str) -> int:
    return 2 if ord(character) > 0xFFFF else 1


def utf16_to_scalar_column(line: str, utf16_column: int) -> int:
    """Map a 1-based UTF-16 start column to a 1-based scalar column on the same line."""
    if utf16_column < 1:
        raise CoordinateError("column must be positive")
    consumed = 0
    for index, character in enumerate(line):
        if consumed == utf16_column - 1:
            return index + 1
        consumed += _utf16_units(character)
        if consumed > utf16_column - 1:
            raise CoordinateError("column points inside a surrogate pair")
    if consumed == utf16_column - 1:
        return len(line) + 1
    raise CoordinateError("column is beyond the end of the line")


def inclusive_utf16_end_to_scalar_end(line: str, utf16_column: int) -> int:
    """Map an inclusive UTF-16 end column to the exclusive scalar end column.

    The inclusive column names the last UTF-16 unit of the range. If that unit is the
    high half of an astral character, the range still covers the whole character.
    """
    if utf16_column < 1:
        raise CoordinateError("column must be positive")
    consumed = 0
    for index, character in enumerate(line):
        consumed += _utf16_units(character)
        if consumed >= utf16_column:
            return index + 2
    raise CoordinateError("inclusive end is beyond the end of the line")


def javaparser_range_to_cir(source: SourceText, native: list[int] | tuple[int, ...]) -> tuple:
    """Convert [begin_line, begin_col, end_line, end_col_inclusive] to CIR coordinates."""
    if native is None or len(native) != 4:
        raise CoordinateError("parser did not report a source range")
    begin_line, begin_column, end_line, end_column = native
    start = utf16_to_scalar_column(source.line(begin_line), begin_column)
    end = inclusive_utf16_end_to_scalar_end(source.line(end_line), end_column)
    if (end_line, end) <= (begin_line, start):
        raise CoordinateError("converted range is empty or reversed")
    return begin_line, start, end_line, end


def scalar_slice(source: SourceText, start_line: int, start_column: int,
                 end_line: int, end_column: int) -> str:
    """Return the text covered by a CIR range, joining lines with LF."""
    if start_line == end_line:
        return source.line(start_line)[start_column - 1:end_column - 1]
    parts = [source.line(start_line)[start_column - 1:]]
    parts += [source.line(number) for number in range(start_line + 1, end_line)]
    parts.append(source.line(end_line)[:end_column - 1])
    return "\n".join(parts)


def scalar_to_utf16_column(line: str, scalar_column: int) -> int:
    """CIR scalar column to Monaco UTF-16 column (both 1-based)."""
    if not 1 <= scalar_column <= len(line) + 1:
        raise CoordinateError("scalar column is outside the line")
    return sum(_utf16_units(character) for character in line[:scalar_column - 1]) + 1


def monaco_range(source: SourceText, start_line: int, start_column: int,
                 end_line: int, end_column: int) -> dict[str, int]:
    """Python mirror of frontend/src/coordinates.ts sourceRange for boundary tests."""
    if (end_line, end_column) <= (start_line, start_column):
        raise CoordinateError("range end must follow its start")
    return {
        "startLineNumber": start_line,
        "startColumn": scalar_to_utf16_column(source.line(start_line), start_column),
        "endLineNumber": end_line,
        "endColumn": scalar_to_utf16_column(source.line(end_line), end_column),
    }
