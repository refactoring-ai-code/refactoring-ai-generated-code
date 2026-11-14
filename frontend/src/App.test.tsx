import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("labels the scaffold without claiming product readiness", () => {
    const html = renderToStaticMarkup(<App />);

    expect(html).toContain("Secure refactoring environment");
    expect(html).toContain("Product workflows remain unavailable");
  });
});
