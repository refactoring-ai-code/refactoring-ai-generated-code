export interface SourceRange {
  startLineNumber: number;
  startColumn: number;
  endLineNumber: number;
  endColumn: number;
}

/** CIR scalar columns -> Monaco UTF-16 columns; no source-byte normalization. */
export function sourceRange(
  source: string,
  startLine: number,
  startColumn: number,
  endLine: number,
  endColumn: number,
): SourceRange {
  if (
    /\r(?!\n)/.test(source) ||
    Array.from(source).some((value) => {
      const point = value.codePointAt(0)!;
      return point >= 0xd800 && point <= 0xdfff;
    })
  )
    throw new Error("INVALID_SOURCE");
  const lines = source.split(/\r?\n/);
  const column = (line: number, scalar: number) => {
    if (
      !Number.isSafeInteger(line) ||
      line < 1 ||
      line > lines.length ||
      !Number.isSafeInteger(scalar) ||
      scalar < 1
    )
      throw new Error("INVALID_RANGE");
    const scalars = Array.from(lines[line - 1]);
    if (scalar > scalars.length + 1) throw new Error("INVALID_RANGE");
    return scalars.slice(0, scalar - 1).join("").length + 1;
  };
  const result = {
    startLineNumber: startLine,
    startColumn: column(startLine, startColumn),
    endLineNumber: endLine,
    endColumn: column(endLine, endColumn),
  };
  if (
    endLine < startLine ||
    (endLine === startLine && endColumn <= startColumn)
  ) {
    throw new Error("INVALID_RANGE");
  }
  return result;
}

export function sourceSegments(
  source: string,
  range: SourceRange,
): [string, string, string] {
  const starts = [0];
  for (let index = 0; index < source.length; index++) {
    if (source[index] === "\n") starts.push(index + 1);
  }
  const start = starts[range.startLineNumber - 1] + range.startColumn - 1;
  const end = starts[range.endLineNumber - 1] + range.endColumn - 1;
  return [source.slice(0, start), source.slice(start, end), source.slice(end)];
}
