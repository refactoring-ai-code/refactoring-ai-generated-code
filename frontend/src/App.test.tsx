// @vitest-environment jsdom
import { webcrypto } from "node:crypto";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { loadWorkspace, type Workspace } from "./workspace";
import { createSourceEditor } from "./monaco";

vi.mock("./monaco", () => ({ createSourceEditor: vi.fn(() => () => {}) }));
(
  globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }
).IS_REACT_ACT_ENVIRONMENT = true;
let host: HTMLDivElement;
let root: Root;
beforeEach(() => {
  vi.stubGlobal("crypto", webcrypto);
  vi.mocked(createSourceEditor).mockClear();
  host = document.createElement("div");
  document.body.appendChild(host);
  root = createRoot(host);
});
afterEach(async () => {
  await act(async () => root.unmount());
  host.remove();
  vi.unstubAllGlobals();
});
async function settle(assertion: () => void) {
  await vi.waitFor(
    async () => {
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
      assertion();
    },
    { timeout: 3000 },
  );
}
async function render(props: Parameters<typeof App>[0] = {}) {
  await act(async () => root.render(<App {...props} />));
  await settle(() =>
    expect(
      host.querySelector('[aria-label="Finding list"], [role="alert"]'),
    ).not.toBeNull(),
  );
}
function checkbox(rule: string) {
  return host.querySelector<HTMLInputElement>(
    `input[aria-label="Select ${rule}"]`,
  )!;
}
function button(text: string) {
  const found = Array.from(host.querySelectorAll("button")).find((item) =>
    item.textContent?.includes(text),
  );
  if (!found) throw new Error(`Button not found: ${text}`);
  return found;
}
async function click(element: HTMLElement) {
  await act(async () => element.click());
}
async function scenario(value: string) {
  const select = host.querySelector("select")!;
  await act(async () => {
    select.value = value;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

describe("first approval fixture UI", () => {
  it("labels synthetic mode and lets a user preview then clear eligible choices without a POST", async () => {
    const request = vi.spyOn(globalThis, "fetch");
    try {
      await render();
      expect(host.textContent).toContain("FIXTURE MODE");
      expect(host.textContent).toContain(
        "No analysis, approval, or refactoring service is connected",
      );
      expect(button("Preview choices").disabled).toBe(true);
      await click(checkbox("fixture:complexity"));
      expect(checkbox("fixture:complexity").checked).toBe(true);
      await click(button("Preview choices"));
      const preview = host.querySelector(
        '[aria-label="Fixture selection preview"]',
      )!;
      expect(preview.textContent).toContain("finding:quality");
      expect(preview.textContent).toContain("not a saved IssueSelection");
      await click(button("Clear selection"));
      expect(checkbox("fixture:complexity").checked).toBe(false);
      expect(
        host.querySelector('[aria-label="Fixture selection preview"]'),
      ).toBeNull();
      expect(request).not.toHaveBeenCalled();
    } finally {
      request.mockRestore();
    }
  });
  it("keeps security, baseline and unresolved choices disabled with an accessible explanation", async () => {
    await render();
    for (const rule of [
      "fixture:security-review",
      "fixture:baseline-review",
      "fixture:unresolved",
    ]) {
      const input = checkbox(rule);
      expect(input.disabled).toBe(true);
      expect(
        document.getElementById(input.getAttribute("aria-describedby")!)
          ?.textContent,
      ).toBeTruthy();
      await click(input);
      expect(input.checked).toBe(false);
    }
    await click(button("Source mapping needs review"));
    expect(
      host.querySelector('[aria-label="Finding details"]')?.textContent,
    ).toContain("No range has been guessed");
    expect(
      host.querySelector('[aria-label="Finding details"]')?.textContent,
    ).toContain("Unknown");
  });
  it("opens each duplicate file with its exact converted range", async () => {
    await render();
    await click(button("Duplicate source locations"));
    await settle(() =>
      expect(vi.mocked(createSourceEditor).mock.calls.at(-1)?.[1].path).toBe(
        "src/Main.java",
      ),
    );
    expect(
      vi.mocked(createSourceEditor).mock.calls.at(-1)?.[1].range.endColumn,
    ).toBe(6);
    await click(button("Location 2"));
    await settle(() =>
      expect(vi.mocked(createSourceEditor).mock.calls.at(-1)?.[1].path).toBe(
        "src/Helper.java",
      ),
    );
    expect(vi.mocked(createSourceEditor).mock.calls.at(-1)?.[1].range).toEqual({
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 7,
    });
    await click(checkbox("fixture:duplication"));
    expect(checkbox("fixture:duplication").checked).toBe(true);
  });
  it("filters findings by category without silently losing chosen IDs", async () => {
    await render();
    await click(checkbox("fixture:complexity"));
    const filter = Array.from(
      host.querySelectorAll('[aria-label="Category filters"] button'),
    ).find((item) => item.textContent?.startsWith("Security"))!;
    await click(filter as HTMLElement);
    expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(1);
    expect(
      host.querySelector('[aria-label="Fixture selection"]')?.textContent,
    ).toContain("01");
    await click(button("All findings"));
    expect(checkbox("fixture:complexity").checked).toBe(true);
  });
  it("searches source paths and offers a working empty-state recovery", async () => {
    await render();
    const input = host.querySelector<HTMLInputElement>('input[type="search"]')!;
    const setValue = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype,
      "value",
    )!.set!;
    await act(async () => {
      setValue.call(input, "src/Helper.java");
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(1);
    await act(async () => {
      setValue.call(input, "missing-source");
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    expect(host.textContent).toContain("No matching findings");
    await click(button("Clear filters"));
    expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(6);
  });
  it("clears old choices when the baseline becomes unavailable", async () => {
    await render();
    await click(checkbox("fixture:complexity"));
    await scenario("baseline");
    await settle(() =>
      expect(host.textContent).toContain("Unavailable test evidence"),
    );
    expect(
      Array.from(
        host.querySelectorAll<HTMLInputElement>('input[type="checkbox"]'),
      ).every((input) => input.disabled && !input.checked),
    ).toBe(true);
    expect(button("Preview choices").disabled).toBe(true);
  });
  it("renders the approved stale-selection error, drops prior choices and recovers", async () => {
    await render();
    await click(checkbox("fixture:complexity"));
    await scenario("error");
    await settle(() =>
      expect(host.querySelector('[role="alert"]')?.textContent).toContain(
        "STALE_SELECTION",
      ),
    );
    expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(0);
    await click(button("Reload fixture"));
    await settle(() => expect(checkbox("fixture:complexity")).not.toBeNull());
    expect(checkbox("fixture:complexity").checked).toBe(false);
  });
  it("does not reflect raw exception data and retries a failed load", async () => {
    const loader = vi
      .fn(loadWorkspace)
      .mockRejectedValueOnce(new Error("private-host-path-and-secret"));
    await render({ loader });
    expect(host.textContent).toContain("INVALID_CONTRACT");
    expect(host.textContent).not.toContain("private-host-path-and-secret");
    await click(button("Reload fixture"));
    await settle(() => expect(checkbox("fixture:complexity")).not.toBeNull());
  });
  it("ignores a late response from a previous scenario", async () => {
    let resolveOld!: (value: Workspace) => void;
    const loader = vi.fn(loadWorkspace).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveOld = resolve;
        }),
    );
    await act(async () =>
      root.render(<App loader={loader} initialScenario="contract" />),
    );
    await scenario("review");
    await settle(() =>
      expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(6),
    );
    await act(async () => resolveOld(await loadWorkspace("contract")));
    expect(host.querySelectorAll('input[type="checkbox"]')).toHaveLength(6);
  });
  it("preserves an exact read-only highlighted fallback if Monaco cannot load", async () => {
    vi.mocked(createSourceEditor).mockImplementationOnce(() => {
      throw new Error("worker load failure");
    });
    await render({ initialScenario: "contract" });
    await settle(() =>
      expect(host.textContent).toContain("Monaco could not load"),
    );
    expect(host.querySelector("mark")?.textContent).toBe("α😀x");
  });
});
