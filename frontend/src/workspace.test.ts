import { describe, expect, it } from "vitest";
import {
  buildWorkspace,
  fixtureSources,
  loadWorkspace,
  scenarioPayload,
  selectionBlocker,
  type Finding,
  type ResultEnvelope,
  type Workspace,
} from "./workspace";
import result from "./contracts/result.json";
import { sourceRange, sourceSegments } from "./coordinates";

const payload = () => scenarioPayload("contract") as ResultEnvelope;
function quality(workspace: Workspace): Finding {
  return workspace.findings.find(
    (finding) => finding.id === "finding:quality",
  )!;
}

describe("CIR scalar coordinates at the Monaco boundary", () => {
  it("maps tabs and astral emoji to UTF-16 without normalizing CRLF", () => {
    const source = fixtureSources.get("file:main")!;
    const range = sourceRange(source, 1, 2, 1, 5);
    expect(range).toEqual({
      startLineNumber: 1,
      startColumn: 2,
      endLineNumber: 1,
      endColumn: 6,
    });
    expect(sourceSegments(source, range)).toEqual(["\t", "α😀x", "\r\nnext\n"]);
    expect(sourceRange(source, 1, 3, 2, 3)).toEqual({
      startLineNumber: 1,
      startColumn: 3,
      endLineNumber: 2,
      endColumn: 3,
    });
    expect(sourceSegments(source, sourceRange(source, 1, 3, 2, 3))[1]).toBe(
      "😀x\r\nne",
    );
  });
  it.each([
    [0, 1, 1, 2],
    [1, 1.5, 1, 2],
    [1, 1, 1, 99],
    [4, 1, 4, 2],
    [2, 1, 1, 2],
    [1, 3, 1, 3],
  ])("rejects invalid range %j", (a, b, c, d) => {
    expect(() => sourceRange("abc\nxy\n", a, b, c, d)).toThrow();
  });
  it.each(["a\rb", "a\ud800b", "a\udc00b"])(
    "rejects untranslatable source bytes",
    (source) => {
      expect(() => sourceRange(source, 1, 1, 1, 2)).toThrow("INVALID_SOURCE");
    },
  );
});

describe("fixture consumer and fail-closed selection", () => {
  it("consumes the unmodified approved envelope and its exact source bytes", async () => {
    const workspace = await loadWorkspace("contract");
    expect(workspace.findings).toHaveLength(2);
    expect(workspace.baselineReady).toBe(true);
    expect(selectionBlocker(quality(workspace), workspace)).toBeNull();
    expect(workspace.views.get("location:main")?.source).toBe(
      "\tα😀x\r\nnext\n",
    );
  });
  it("resolves both duplicate files and independent ranges without altering the approved fixture", async () => {
    const original = JSON.stringify(result);
    const workspace = await loadWorkspace("review");
    const duplicate = workspace.findings.find(
      (finding) => finding.category === "DUPLICATION",
    )!;
    expect(selectionBlocker(duplicate, workspace)).toBeNull();
    expect(
      duplicate.location_ids.map((id) => workspace.views.get(id)?.path),
    ).toEqual(["src/Main.java", "src/Helper.java"]);
    const helper = workspace.views.get("location:helper")!;
    expect(sourceSegments(helper.source, helper.range)[1]).toBe("helper");
    expect(JSON.stringify(result)).toBe(original);
  });
  it("never enables security or baseline findings even with a forged ELIGIBLE flag", async () => {
    const workspace = await loadWorkspace("review");
    for (const finding of workspace.findings.filter(
      (item) => item.classification !== "QUALITY_REFACTOR",
    )) {
      finding.eligibility = "ELIGIBLE";
      expect(selectionBlocker(finding, workspace)).toContain(
        "Only QUALITY_REFACTOR",
      );
    }
  });
  it("rejects an inconsistent security category even if classification claims quality", async () => {
    const workspace = await loadWorkspace("contract");
    quality(workspace).category = "SECURITY";
    expect(selectionBlocker(quality(workspace), workspace)).toContain(
      "categories cannot be selected",
    );
  });
  it("keeps two distinct ranges in the same file independently addressable", async () => {
    const data = scenarioPayload("review") as ResultEnvelope;
    const main = data.data.records.find(
      (item) => item.kind === "SourceLocation" && item.id === "location:main",
    )!;
    const second = data.data.records.find(
      (item) => item.kind === "SourceLocation" && item.id === "location:helper",
    )!;
    Object.assign(second, main, {
      id: "location:helper",
      start_line: 2,
      start_column: 1,
      end_line: 2,
      end_column: 5,
    });
    const workspace = await buildWorkspace(data);
    const duplicate = workspace.findings.find(
      (item) => item.category === "DUPLICATION",
    )!;
    expect(selectionBlocker(duplicate, workspace)).toBeNull();
    expect(workspace.views.get("location:main")?.path).toBe(
      workspace.views.get("location:helper")?.path,
    );
    const view = workspace.views.get("location:helper")!;
    expect(sourceSegments(view.source, view.range)[1]).toBe("next");
  });
  it("shows unresolved source/unknown confidence without inventing a range", async () => {
    const workspace = await loadWorkspace("review");
    const finding = workspace.findings.find(
      (item) => item.eligibility === "UNRESOLVED",
    )!;
    expect(finding.confidence.value).toBeNull();
    expect(workspace.views.has("location:ui-unresolved")).toBe(false);
    expect(workspace.unavailable.get("location:ui-unresolved")).toContain(
      "unresolved",
    );
    expect(selectionBlocker(finding, workspace)).not.toBeNull();
  });
  it.each(["FAILED", "UNVERIFIED"] as const)(
    "blocks a %s baseline",
    async (outcome) => {
      const data = payload();
      const baseline = data.data.records.find(
        (record) =>
          record.kind === "TestResult" && record.id === "test:baseline",
      )!;
      Object.assign(baseline, { outcome });
      const workspace = await buildWorkspace(data);
      expect(selectionBlocker(quality(workspace), workspace)).toContain(
        "baseline",
      );
    },
  );
  it.each([
    { total: 0, passed: 0 },
    { skipped: 1 },
    { environment_sha256: null },
    { evidence_ids: [] },
    { subject_sha256: "f".repeat(64) },
  ])(
    "blocks incomplete, skipped, stale or empty baseline evidence",
    async (change) => {
      const data = payload();
      Object.assign(
        data.data.records.find((record) => record.id === "test:baseline")!,
        change,
      );
      const workspace = await buildWorkspace(data);
      expect(workspace.baselineReady).toBe(false);
    },
  );
  it("disables all choices in the explicit unavailable-baseline scenario", async () => {
    const workspace = await loadWorkspace("baseline");
    expect(
      workspace.findings.every((finding) =>
        selectionBlocker(finding, workspace),
      ),
    ).toBe(true);
  });
  it.each(["RESOLVED", "SUPPRESSED", "UNVERIFIED"] as const)(
    "blocks a %s quality finding",
    async (status) => {
      const workspace = await loadWorkspace("contract");
      quality(workspace).status = status;
      expect(selectionBlocker(quality(workspace), workspace)).toContain(
        "open findings",
      );
    },
  );
  it("blocks stale findings, missing references and partial duplicate locations", async () => {
    const workspace = await loadWorkspace("review");
    const finding = quality(workspace);
    finding.subject_sha256 = "e".repeat(64);
    expect(selectionBlocker(finding, workspace)).toContain(
      "different source snapshot",
    );
    finding.subject_sha256 = workspace.bundle.scope.baseline_sha256;
    finding.location_ids = ["location:missing"];
    expect(selectionBlocker(finding, workspace)).toContain("missing");
    const duplicate = workspace.findings.find(
      (item) => item.category === "DUPLICATION",
    )!;
    duplicate.location_ids = ["location:main", "location:main"];
    expect(selectionBlocker(duplicate, workspace)).toContain(
      "Both duplicate locations",
    );
  });
  it("rejects unconfirmed evidence and protected test targets", async () => {
    const workspace = await loadWorkspace("contract");
    const evidence = workspace.bundle.records.find(
      (record) =>
        record.kind === "Evidence" && record.id === "evidence:analysis",
    )!;
    Object.assign(evidence, {
      producer_kind: "LLM",
      verification: "UNCONFIRMED",
    });
    expect(selectionBlocker(quality(workspace), workspace)).toContain(
      "evidence",
    );
    Object.assign(evidence, {
      producer_kind: "DETERMINISTIC_TOOL",
      verification: "VERIFIED",
    });
    workspace.bundle.files[0].protected_test = true;
    expect(selectionBlocker(quality(workspace), workspace)).toContain(
      "protected",
    );
  });
  it("never highlights source content whose actual bytes do not match the manifest", async () => {
    const sources = new Map(fixtureSources);
    sources.set("file:main", "tampered\n");
    const workspace = await buildWorkspace(payload(), sources);
    expect(workspace.views.has("location:main")).toBe(false);
    expect(selectionBlocker(quality(workspace), workspace)).toContain(
      "Source bytes",
    );
  });
  it("rejects out-of-bounds source mappings without guessing", async () => {
    const data = payload();
    Object.assign(
      data.data.records.find((record) => record.id === "location:main")!,
      { end_column: 100 },
    );
    const workspace = await buildWorkspace(data);
    expect(workspace.unavailable.get("location:main")).toContain("outside");
    expect(selectionBlocker(quality(workspace), workspace)).not.toBeNull();
  });
  it.each([
    (data: ResultEnvelope) => Object.assign(data, { schema_version: "2.0.0" }),
    (data: ResultEnvelope) => Object.assign(data.data, { mode: "INTERCHANGE" }),
    (data: ResultEnvelope) =>
      Object.assign(data, { next_cursor: "another-page" }),
    (data: ResultEnvelope) =>
      Object.assign(data.data.records[0], { unexpected: true }),
    (data: ResultEnvelope) => data.data.records.push(data.data.records[0]),
  ])(
    "rejects unsupported or incomplete envelopes before rendering",
    async (mutate) => {
      const data = payload();
      mutate(data);
      await expect(buildWorkspace(data)).rejects.toThrow("INVALID_CONTRACT");
    },
  );
  it("uses the approved stale-selection error and no fake successful response", async () => {
    await expect(loadWorkspace("error")).rejects.toThrow("STALE_SELECTION");
    expect(scenarioPayload("review")).not.toBe(result);
  });
});
