import { readFile, writeFile, mkdir } from "node:fs/promises";
import { compile } from "json-schema-to-typescript";

// Generated consumer artifacts let the existing frontend-only Docker build stay isolated.
// The repository sources remain authoritative; CI rejects stale copies/types.
const root = new URL("../../", import.meta.url);
const output = new URL("../src/contracts/", import.meta.url);
const sources = {
  "schema.json": "backend/core/schemas/cir-1.0.0.schema.json",
  "result.json": "docs/contracts/examples/result.json",
  "selection.json": "docs/contracts/examples/issue-selection.json",
  "error.json": "docs/contracts/examples/error.json",
};
const artifacts = new Map();
for (const [name, path] of Object.entries(sources)) {
  artifacts.set(name, await readFile(new URL(path, root)));
}
const api = JSON.parse(
  await readFile(new URL("docs/contracts/openapi-1.0.0.json", root), "utf8"),
);
const schema = JSON.parse(artifacts.get("schema.json"));
// The approved exports must share their complete definition registry.
const apiDefinitions = JSON.parse(
  JSON.stringify(api.components.schemas).replaceAll(
    "#/components/schemas/",
    "#/$defs/",
  ),
);
if (JSON.stringify(apiDefinitions) !== JSON.stringify(schema.$defs)) {
  throw new Error("OpenAPI and CIR definition registries disagree");
}
const registry = {
  title: "UIContracts",
  type: "object",
  additionalProperties: false,
  properties: {
    result: { $ref: "#/$defs/ResultEnvelope" },
    error: { $ref: "#/$defs/ErrorEnvelope" },
    selection: { $ref: "#/$defs/IssueSelection" },
  },
  required: ["result", "error", "selection"],
  $defs: schema.$defs,
};
artifacts.set(
  "types.d.ts",
  Buffer.from(
    await compile(registry, "UIContracts", {
      bannerComment:
        "/* Generated from approved CIR/OpenAPI 1.0.0. Run npm run contracts:sync; do not edit. */",
      unknownAny: true,
      additionalProperties: false,
    }),
  ),
);
if (process.argv.includes("--check")) {
  for (const [name, bytes] of artifacts) {
    if (!bytes.equals(await readFile(new URL(name, output)))) {
      throw new Error(
        `Stale generated contract artifact: ${name}. Run npm run contracts:sync.`,
      );
    }
  }
  console.log(
    "Approved CIR/OpenAPI types and fixture copies match their canonical sources.",
  );
} else {
  await mkdir(output, { recursive: true });
  for (const [name, bytes] of artifacts)
    await writeFile(new URL(name, output), bytes);
  console.log(
    "Generated CIR/OpenAPI consumer types and byte-identical fixture copies.",
  );
}
