import Ajv2020 from "ajv/dist/2020";

import schema from "./contracts/schema.json";
import resultFixture from "./contracts/result.json";
import selectionFixture from "./contracts/selection.json";
import errorFixture from "./contracts/error.json";
import type { UIContracts } from "./contracts/types";
import { sourceRange, type SourceRange } from "./coordinates";

export type ResultEnvelope = UIContracts["result"];
export type Bundle = ResultEnvelope["data"];
export type Record = Bundle["records"][number];
export type Finding = Extract<Record, { kind: "Finding" }>;
export type Location = Extract<Record, { kind: "SourceLocation" }>;
export type Scenario = "contract" | "review" | "baseline" | "error";

// These are the exact UTF-8 strings from tests/contracts/build_fixtures.py.
// They are synthetic coordinate samples, not real Java analysis or uploaded files.
export const fixtureSources = new Map([
  ["file:main", "\tα😀x\r\nnext\n"],
  ["file:helper", "helper()\n"],
]);
const ajv = new Ajv2020({ strict: false, allErrors: true });
ajv.addSchema(schema);
const reference = (name: string) => ({
  $ref: `urn:genesis:cir:1.0.0#/$defs/${name}`,
});
const validateResult = ajv.compile<ResultEnvelope>(reference("ResultEnvelope"));
const validateSelection = ajv.compile<UIContracts["selection"]>(
  reference("IssueSelection"),
);
const validateError = ajv.compile<UIContracts["error"]>(
  reference("ErrorEnvelope"),
);

export class FixtureError extends Error {
  constructor(public code: "INVALID_CONTRACT" | "STALE_SELECTION") {
    super(code);
  }
}
export interface SourceView {
  location: Location;
  path: string;
  source: string;
  range: SourceRange;
}
export interface Workspace {
  bundle: Bundle;
  findings: Finding[];
  baselineReady: boolean;
  views: Map<string, SourceView>;
  unavailable: Map<string, string>;
}
function sameScope(a: Record["scope"], b: Record["scope"]) {
  return (Object.keys(b) as (keyof typeof b)[]).every(
    (key) => a[key] === b[key],
  );
}
function current(record: Record, bundle: Bundle) {
  return (
    sameScope(record.scope, bundle.scope) &&
    record.subject_sha256 === bundle.scope.baseline_sha256
  );
}
function independentEvidence(ids: string[], bundle: Bundle) {
  return ids.some((id) =>
    bundle.records.some(
      (record) =>
        record.kind === "Evidence" &&
        record.id === id &&
        current(record, bundle) &&
        record.verification === "VERIFIED" &&
        record.producer_kind !== "LLM" &&
        ["MASKED", "NO_SENSITIVE_CONTENT"].includes(record.redaction) &&
        bundle.artifacts.some(
          (artifact) =>
            artifact.id === record.artifact_id &&
            ["MASKED", "NO_SENSITIVE_CONTENT"].includes(artifact.redaction),
        ),
    ),
  );
}
export async function fileHash(source: string) {
  const bytes = new TextEncoder().encode(source);
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(hash), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

/** Only fixture envelopes are accepted here. This is deliberately not a live API client. */
export async function buildWorkspace(
  payload: unknown,
  sources = fixtureSources,
): Promise<Workspace> {
  if (
    !validateResult(payload) ||
    payload.data.mode !== "FIXTURE" ||
    payload.next_cursor !== null
  ) {
    throw new FixtureError("INVALID_CONTRACT");
  }
  const bundle = payload.data;
  const allIds = [
    ...bundle.records,
    ...bundle.files,
    ...bundle.artifacts,
    ...bundle.test_suites,
    ...bundle.attempts,
  ].map((item) => item.id);
  if (new Set(allIds).size !== allIds.length)
    throw new FixtureError("INVALID_CONTRACT");
  const views = new Map<string, SourceView>();
  const unavailable = new Map<string, string>();
  const hashes = new Map<string, string>();
  for (const file of bundle.files) {
    const source = sources.get(file.id);
    if (source !== undefined) hashes.set(file.id, await fileHash(source));
  }
  for (const location of bundle.records.filter(
    (r): r is Location => r.kind === "SourceLocation",
  )) {
    const file = bundle.files.find((f) => f.id === location.file_id);
    const source = location.file_id ? sources.get(location.file_id) : undefined;
    if (location.resolution !== "RESOLVED") {
      unavailable.set(location.id, "Source location is unresolved.");
      continue;
    }
    if (
      !current(location, bundle) ||
      !file ||
      file.is_symlink ||
      file.subject_sha256 !== bundle.scope.baseline_sha256 ||
      file.path !== location.path ||
      file.sha256 !== location.file_sha256 ||
      hashes.get(file.id) !== file.sha256 ||
      source === undefined
    ) {
      unavailable.set(
        location.id,
        "Source bytes or snapshot binding could not be verified.",
      );
      continue;
    }
    try {
      if (
        location.start_line === null ||
        location.start_column === null ||
        location.end_line === null ||
        location.end_column === null
      )
        throw new Error("INVALID_RANGE");
      views.set(location.id, {
        location,
        path: file.path,
        source,
        range: sourceRange(
          source,
          location.start_line,
          location.start_column,
          location.end_line,
          location.end_column,
        ),
      });
    } catch {
      unavailable.set(
        location.id,
        "Source range is outside the verified file.",
      );
    }
  }
  const baselineReady = bundle.records.some((record) => {
    if (record.kind !== "TestResult" || !current(record, bundle)) return false;
    const suite = bundle.test_suites.find(
      (item) =>
        item.id === record.suite_id && item.sha256 === record.suite_sha256,
    );
    return (
      record.execution_status === "COMPLETED" &&
      record.outcome === "PASSED" &&
      record.total !== null &&
      record.total > 0 &&
      record.passed === record.total &&
      record.failed === 0 &&
      record.skipped === 0 &&
      record.environment_sha256 !== null &&
      suite?.case_ids.length === record.total &&
      independentEvidence(record.evidence_ids, bundle)
    );
  });
  return {
    bundle,
    findings: bundle.records.filter((r): r is Finding => r.kind === "Finding"),
    baselineReady,
    views,
    unavailable,
  };
}

export function selectionBlocker(
  finding: Finding,
  workspace: Workspace,
): string | null {
  if (finding.classification !== "QUALITY_REFACTOR")
    return "Only QUALITY_REFACTOR findings can be selected.";
  if (["SECURITY", "BASELINE"].includes(finding.category))
    return "Security and baseline categories cannot be selected.";
  if (finding.eligibility !== "ELIGIBLE")
    return finding.eligibility_reason ?? "Eligibility is unresolved.";
  if (finding.status !== "OPEN") return "Only open findings can be selected.";
  if (!workspace.baselineReady)
    return "A verified, passing baseline is required.";
  if (!current(finding, workspace.bundle))
    return "Finding belongs to a different source snapshot.";
  if (!independentEvidence(finding.evidence_ids, workspace.bundle))
    return "Independent verified evidence is unavailable.";
  if (
    finding.category === "DUPLICATION" &&
    new Set(finding.location_ids).size < 2
  )
    return "Both duplicate locations are required.";
  for (const id of finding.location_ids) {
    const view = workspace.views.get(id);
    if (!view)
      return workspace.unavailable.get(id) ?? "Source location is missing.";
    const file = workspace.bundle.files.find(
      (entry) => entry.id === view.location.file_id,
    );
    if (file?.frozen || file?.protected_test)
      return "Frozen or protected inputs cannot be selected.";
  }
  return null;
}

export function scenarioPayload(scenario: Exclude<Scenario, "error">): unknown {
  // Additional UI-only cases are copies; approved examples are never modified.
  const input: unknown = structuredClone(resultFixture);
  if (!validateResult(input)) throw new FixtureError("INVALID_CONTRACT");
  const result = input;
  if (scenario !== "contract") {
    const finding = result.data.records.find(
      (r): r is Finding => r.kind === "Finding" && r.id === "finding:quality",
    )!;
    const location = result.data.records.find(
      (r): r is Location => r.kind === "SourceLocation",
    )!;
    result.data.records.push(
      {
        ...structuredClone(finding),
        id: "finding:ui-quality",
        category: "QUALITY",
        rule_id: "fixture:quality",
      },
      {
        ...structuredClone(finding),
        id: "finding:ui-duplicate",
        category: "DUPLICATION",
        rule_id: "fixture:duplication",
        location_ids: ["location:main", "location:helper"],
      },
      {
        ...structuredClone(finding),
        id: "finding:ui-baseline",
        category: "BASELINE",
        classification: "BASELINE",
        rule_id: "fixture:baseline-review",
        eligibility: "INELIGIBLE",
        eligibility_reason:
          "Baseline observations are not quality refactoring tasks.",
      },
      {
        ...structuredClone(location),
        id: "location:ui-unresolved",
        resolution: "UNRESOLVED",
        reason: "Synthetic unresolved source mapping.",
        path: null,
        file_id: null,
        file_sha256: null,
        start_line: null,
        start_column: null,
        end_line: null,
        end_column: null,
        symbol_id: null,
      },
      {
        ...structuredClone(finding),
        id: "finding:ui-unresolved",
        rule_id: "fixture:unresolved",
        status: "UNVERIFIED",
        eligibility: "UNRESOLVED",
        eligibility_reason: "Source mapping is unresolved; review is required.",
        confidence: { value: null, reason: "Synthetic unknown confidence." },
        location_ids: ["location:ui-unresolved"],
      },
    );
  }
  if (scenario === "baseline") {
    for (const record of result.data.records) {
      if (record.kind === "TestResult" && record.id === "test:baseline") {
        Object.assign(record, {
          execution_status: "UNAVAILABLE",
          outcome: "UNVERIFIED",
          total: null,
          passed: null,
          failed: null,
          skipped: null,
          environment_sha256: null,
          reason: "Synthetic unavailable baseline.",
        });
      }
    }
  }
  return result;
}
export async function loadWorkspace(scenario: Scenario) {
  if (scenario === "error") {
    if (!validateError(errorFixture))
      throw new FixtureError("INVALID_CONTRACT");
    throw new FixtureError("STALE_SELECTION");
  }
  if (
    !validateSelection(selectionFixture) ||
    !sameScope(selectionFixture.scope, resultFixture.data.scope)
  )
    throw new FixtureError("INVALID_CONTRACT");
  return buildWorkspace(scenarioPayload(scenario));
}
