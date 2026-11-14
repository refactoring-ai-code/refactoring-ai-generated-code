import { useEffect, useMemo, useState } from "react";
import { SourcePane } from "./SourcePane";
import {
  FixtureError,
  loadWorkspace,
  selectionBlocker,
  type Finding,
  type Scenario,
  type Workspace,
} from "./workspace";

const categories = [
  "ALL",
  "QUALITY",
  "COMPLEXITY",
  "DUPLICATION",
  "SECURITY",
  "BASELINE",
] as const;
type Category = (typeof categories)[number];
const label = (value: string) => value.charAt(0) + value.slice(1).toLowerCase();
const names: { [key: string]: string } = {
  "fixture:complexity": "Complexity observation",
  "fixture:security-review": "Security review required",
  "fixture:quality": "Quality observation",
  "fixture:duplication": "Duplicate source locations",
  "fixture:baseline-review": "Baseline observation",
  "fixture:unresolved": "Source mapping needs review",
};
const title = (finding: Finding) => names[finding.rule_id] ?? finding.rule_id;

export function App({
  initialScenario = "review",
  loader = loadWorkspace,
}: {
  initialScenario?: Scenario;
  loader?: typeof loadWorkspace;
}) {
  const [scenario, setScenario] = useState<Scenario>(initialScenario);
  const [attempt, setAttempt] = useState(0);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<Category>("ALL");
  const [search, setSearch] = useState("");
  const [activeId, setActiveId] = useState<string | null>(null);
  const [locationId, setLocationId] = useState<string | null>(null);
  const [chosen, setChosen] = useState<string[]>([]);
  const [preview, setPreview] = useState(false);
  useEffect(() => {
    let cancelled = false;
    setWorkspace(null);
    setError(null);
    setChosen([]);
    setPreview(false);
    setActiveId(null);
    setLocationId(null);
    loader(scenario)
      .then((result) => {
        if (!cancelled) setWorkspace(result);
      })
      .catch((reason: unknown) => {
        if (!cancelled)
          setError(
            reason instanceof FixtureError ? reason.code : "INVALID_CONTRACT",
          );
      });
    return () => {
      cancelled = true;
    };
  }, [scenario, attempt, loader]);
  const findings = workspace?.findings ?? [];
  const visible = useMemo(
    () =>
      findings.filter((finding) => {
        const paths = workspace
          ? finding.location_ids
              .map((id) => workspace.views.get(id)?.path ?? "unresolved")
              .join(" ")
          : "";
        return (
          (category === "ALL" || finding.category === category) &&
          `${title(finding)} ${finding.id} ${finding.rule_id} ${paths}`
            .toLowerCase()
            .includes(search.toLowerCase())
        );
      }),
    [findings, category, search, workspace],
  );
  const active =
    visible.find((finding) => finding.id === activeId) ?? visible[0];
  const currentLocation =
    active?.location_ids.find((id) => id === locationId) ??
    active?.location_ids[0];
  const view = currentLocation
    ? workspace?.views.get(currentLocation)
    : undefined;
  const selected = workspace
    ? findings.filter(
        (finding) =>
          chosen.includes(finding.id) && !selectionBlocker(finding, workspace),
      )
    : [];
  const eligibleCount = workspace
    ? findings.filter((finding) => !selectionBlocker(finding, workspace)).length
    : 0;
  const toggle = (finding: Finding) => {
    if (!workspace || selectionBlocker(finding, workspace)) return;
    setChosen((ids) =>
      ids.includes(finding.id)
        ? ids.filter((id) => id !== finding.id)
        : [...ids, finding.id],
    );
    setPreview(false);
  };
  return (
    <div className="app-shell">
      <a className="skip-link" href="#findings">
        Skip to findings
      </a>
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brand-mark" aria-hidden="true">
            g.
          </span>
          <span>
            genesis<span className="brand-tag">WORKSPACE</span>
          </span>
        </a>
        <span className="workspace-name">
          Contract workspace <span aria-hidden="true">/</span> First approval
        </span>
        <span className="connection">
          <span className="status-dot" />
          Backend disconnected
        </span>
      </header>
      <main>
        <section className="intro">
          <div>
            <p className="eyebrow">
              APPROVAL 01 <span>/</span> ISSUE EXPLORER
            </p>
            <h1>Review before you refactor.</h1>
            <p className="intro-copy">
              Inspect the evidence. Choose the quality findings worth changing.
            </p>
          </div>
          <div className="snapshot-chip">
            <span className="snapshot-icon" aria-hidden="true">
              ◇
            </span>
            <div>
              <strong>Original V0</strong>
              <span>Read-only source snapshot</span>
            </div>
          </div>
        </section>
        <section className="fixture-banner" aria-label="Fixture mode notice">
          <span className="fixture-badge">FIXTURE MODE</span>
          <p>
            Synthetic CIR 1.0.0 examples. No analysis, approval, or refactoring
            service is connected.
          </p>
          <label className="scenario-label">
            Fixture scenario
            <select
              aria-label="Fixture scenario"
              value={scenario}
              onChange={(event) => {
                setCategory("ALL");
                setSearch("");
                setScenario(event.target.value as Scenario);
              }}
            >
              <option value="review">UI coverage cases</option>
              <option value="contract">Approved API sample</option>
              <option value="baseline">Unavailable baseline</option>
              <option value="error">Stale-selection error</option>
            </select>
          </label>
        </section>
        <div className="review-meta">
          <span>
            <span className="status-dot" />
            {scenario === "contract"
              ? "Approved contract sample"
              : "UI-only cases derived from the approved sample"}
          </span>
          <span>Source sample · tabs, Unicode &amp; CRLF</span>
        </div>
        {error ? (
          <section className="empty-state error-state" role="alert">
            <span className="empty-icon" aria-hidden="true">
              !
            </span>
            <p className="eyebrow">{error}</p>
            <h2>
              {error === "STALE_SELECTION"
                ? "These findings have changed."
                : "This fixture could not be verified."}
            </h2>
            <p>
              {error === "STALE_SELECTION"
                ? "A fresh selection is required. Previous choices have been cleared."
                : "No selection was retained. Check the contract and source snapshot before continuing."}
            </p>
            <button
              className="primary-button"
              onClick={() => {
                if (scenario === "error") setScenario("review");
                else setAttempt((value) => value + 1);
              }}
            >
              Reload fixture
            </button>
          </section>
        ) : !workspace ? (
          <section className="empty-state" role="status">
            <h2>Verifying fixture snapshot…</h2>
            <p>Checking contract shape, source hashes and locations.</p>
          </section>
        ) : (
          <>
            <div className="explorer-layout">
              <aside className="filters" aria-label="Finding categories">
                <p className="panel-eyebrow">FINDINGS</p>
                <h2>By category</h2>
                <nav aria-label="Category filters">
                  {categories.map((item) => {
                    const count = findings.filter(
                      (finding) => item === "ALL" || finding.category === item,
                    ).length;
                    return (
                      <button
                        key={item}
                        className={
                          category === item
                            ? "filter-button active"
                            : "filter-button"
                        }
                        aria-pressed={category === item}
                        onClick={() => {
                          setCategory(item);
                          setActiveId(null);
                          setLocationId(null);
                        }}
                      >
                        <span>
                          <span
                            className={`category-dot ${item.toLowerCase()}`}
                            aria-hidden="true"
                          />
                          {item === "ALL" ? "All findings" : label(item)}
                        </span>
                        <span className="count">{count}</span>
                      </button>
                    );
                  })}
                </nav>
                <div className="filter-note">
                  <strong>Selection is deliberate.</strong>
                  <p>
                    Only eligible quality findings can be selected. Security and
                    baseline observations stay in review.
                  </p>
                </div>
                <div
                  className={`baseline-card ${workspace.baselineReady ? "" : "unavailable"}`}
                >
                  <p className="panel-eyebrow">BASELINE · FIXTURE</p>
                  <strong>
                    {workspace.baselineReady ? "Passed" : "Unverified"}
                  </strong>
                  <p>
                    {workspace.baselineReady
                      ? "Synthetic passing test evidence."
                      : "Unavailable test evidence. All selections are disabled."}
                  </p>
                </div>
              </aside>
              <section
                className="finding-list"
                id="findings"
                aria-label="Finding list"
              >
                <div className="list-heading">
                  <div>
                    <h2>
                      Findings <span>{findings.length}</span>
                    </h2>
                    <p>{eligibleCount} eligible for a fixture selection</p>
                  </div>
                  <span className="read-only-tag">V0</span>
                </div>
                <label className="search-box">
                  <svg viewBox="0 0 20 20" aria-hidden="true">
                    <circle cx="8.5" cy="8.5" r="5.5" />
                    <path d="m13 13 4 4" />
                  </svg>
                  <span className="sr-only">Search findings or files</span>
                  <input
                    type="search"
                    placeholder="Search findings or files…"
                    value={search}
                    onChange={(event) => {
                      setSearch(event.target.value);
                      setActiveId(null);
                      setLocationId(null);
                    }}
                  />
                </label>
                <p className="list-count" aria-live="polite">
                  {visible.length}{" "}
                  {visible.length === 1 ? "finding" : "findings"} shown
                </p>
                <div className="finding-cards">
                  {visible.map((finding) => {
                    const blocker = selectionBlocker(finding, workspace);
                    const reasonId = `reason-${finding.id}`;
                    return (
                      <article
                        key={finding.id}
                        className={`finding-card ${active?.id === finding.id ? "inspecting" : ""} ${chosen.includes(finding.id) ? "chosen" : ""}`}
                      >
                        <div className="finding-card-top">
                          <span
                            className={`category-label ${finding.category.toLowerCase()}`}
                          >
                            {label(finding.category)}
                          </span>
                          <label className="choice">
                            <input
                              type="checkbox"
                              aria-label={`Select ${finding.rule_id}`}
                              aria-describedby={reasonId}
                              disabled={!!blocker}
                              checked={selected.some(
                                (item) => item.id === finding.id,
                              )}
                              onChange={() => toggle(finding)}
                            />
                            <span className="sr-only">Select finding</span>
                          </label>
                        </div>
                        <button
                          className="inspect-button"
                          aria-pressed={active?.id === finding.id}
                          onClick={() => {
                            setActiveId(finding.id);
                            setLocationId(null);
                          }}
                        >
                          <strong>{title(finding)}</strong>
                          <span>
                            {finding.location_ids
                              .map(
                                (id) =>
                                  workspace.views.get(id)?.path ??
                                  "Unresolved source",
                              )
                              .join(" · ")}
                          </span>
                          <span className="rule-id">
                            {finding.rule_id} <span aria-hidden="true">↗</span>
                          </span>
                        </button>
                        <p
                          className={`eligibility ${blocker ? "blocked" : ""}`}
                          id={reasonId}
                        >
                          {blocker ?? "Eligible for quality refactoring"}
                        </p>
                      </article>
                    );
                  })}
                </div>
                {!visible.length && (
                  <div className="no-results">
                    <h3>No matching findings</h3>
                    <p>Try another category or search term.</p>
                    <button
                      className="text-button"
                      onClick={() => {
                        setSearch("");
                        setCategory("ALL");
                      }}
                    >
                      Clear filters
                    </button>
                  </div>
                )}
              </section>
              <section className="finding-detail" aria-label="Finding details">
                {active ? (
                  <>
                    <div className="detail-heading">
                      <p className="panel-eyebrow">SOURCE INSPECTION</p>
                      <span
                        className={`category-label ${active.category.toLowerCase()}`}
                      >
                        {label(active.category)}
                      </span>
                    </div>
                    <h2>{title(active)}</h2>
                    <p className="detail-description">
                      {active.category === "DUPLICATION"
                        ? "Inspect both source ranges before choosing this fixture finding."
                        : "Review the source-bound observation and its eligibility before making a choice."}
                    </p>
                    <div
                      className="location-tabs"
                      role="group"
                      aria-label="Source locations"
                    >
                      {active.location_ids.map((id, index) => (
                        <button
                          key={id}
                          aria-pressed={currentLocation === id}
                          onClick={() => setLocationId(id)}
                        >
                          <span>
                            {active.location_ids.length > 1
                              ? `Location ${index + 1}`
                              : "Source location"}
                          </span>
                          <small>
                            {workspace.views.get(id)?.path ?? "Unresolved"}
                          </small>
                        </button>
                      ))}
                    </div>
                    {view ? (
                      <SourcePane key={view.location.id} view={view} />
                    ) : (
                      <div className="unresolved-source" role="status">
                        <strong>Source unavailable</strong>
                        <p>
                          {currentLocation
                            ? (workspace.unavailable.get(currentLocation) ??
                              "The referenced location is missing.")
                            : "No source location was provided."}
                        </p>
                        <p>No range has been guessed.</p>
                      </div>
                    )}
                    <dl className="evidence-grid">
                      <div>
                        <dt>Classification</dt>
                        <dd>{active.classification}</dd>
                      </div>
                      <div>
                        <dt>Eligibility</dt>
                        <dd>{active.eligibility}</dd>
                      </div>
                      <div>
                        <dt>Confidence</dt>
                        <dd>
                          {active.confidence.value === null
                            ? "Unknown"
                            : `${Math.round(active.confidence.value * 100)}% · synthetic`}
                        </dd>
                      </div>
                      <div>
                        <dt>Tool</dt>
                        <dd>
                          {active.tool.tool_id} ·{" "}
                          {active.tool.version ?? "Unknown version"}
                        </dd>
                      </div>
                    </dl>
                    <div className="evidence-note">
                      <span aria-hidden="true">↳</span>
                      <div>
                        <strong>Evidence stays attached.</strong>
                        <p>{active.evidence_ids.join(", ")}</p>
                        <p>
                          Synthetic evidence demonstrates the contract; it is
                          not a real analyzer result.
                        </p>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="no-results">
                    <h2>Nothing to inspect</h2>
                    <p>Choose a finding from the list.</p>
                  </div>
                )}
              </section>
            </div>
            <section className="selection-bar" aria-label="Fixture selection">
              <div>
                <span className="selection-count">
                  {selected.length.toString().padStart(2, "0")}
                </span>
                <div>
                  <strong>
                    {selected.length === 1
                      ? "finding selected"
                      : "findings selected"}
                  </strong>
                  <p>Local choices only. No approval will be saved or sent.</p>
                </div>
              </div>
              <div>
                <button
                  className="text-button"
                  disabled={!selected.length}
                  onClick={() => {
                    setChosen([]);
                    setPreview(false);
                  }}
                >
                  Clear selection
                </button>
                <button
                  className="primary-button"
                  disabled={!selected.length}
                  onClick={() => setPreview((value) => !value)}
                  aria-expanded={preview}
                >
                  Preview choices <span aria-hidden="true">→</span>
                </button>
              </div>
            </section>
            {preview && (
              <section
                className="selection-preview"
                aria-label="Fixture selection preview"
              >
                <p className="eyebrow">FIXTURE SELECTION PREVIEW</p>
                <h2>Your choices, before any changes.</h2>
                <p>
                  This is a local draft, not a saved IssueSelection or
                  authenticated approval. API integration belongs to
                  F08-INTEGRATE.
                </p>
                <ul>
                  {selected.map((finding) => (
                    <li key={finding.id}>
                      {title(finding)} <code>{finding.id}</code>
                    </li>
                  ))}
                </ul>
                <dl>
                  <dt>Analysis</dt>
                  <dd>{workspace.bundle.scope.analysis_id}</dd>
                  <dt>Immutable version</dt>
                  <dd>{workspace.bundle.scope.version_id}</dd>
                  <dt>Source snapshot SHA-256</dt>
                  <dd className="hash">
                    {workspace.bundle.scope.baseline_sha256}
                  </dd>
                </dl>
              </section>
            )}
          </>
        )}
        <footer className="page-footer">
          <span>
            GENESIS <span aria-hidden="true">/</span> Secure refactoring,
            considered.
          </span>
          <span>CIR 1.0.0 · Fixture workspace</span>
        </footer>
      </main>
    </div>
  );
}
