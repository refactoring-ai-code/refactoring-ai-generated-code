import { useEffect, useRef, useState } from "react";
import { sourceSegments } from "./coordinates";
import type { SourceView } from "./workspace";

export function SourcePane({ view }: { view: SourceView }) {
  const container = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"loading" | "ready" | "failed">("loading");
  useEffect(() => {
    let cancelled = false;
    let dispose: (() => void) | undefined;
    setState("loading");
    import("./monaco")
      .then(({ createSourceEditor }) => {
        if (!cancelled && container.current) {
          dispose = createSourceEditor(container.current, view);
          setState("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setState("failed");
      });
    return () => {
      cancelled = true;
      dispose?.();
    };
  }, [view]);
  const [before, highlighted, after] = sourceSegments(view.source, view.range);
  return (
    <section
      className="source-pane"
      aria-label={`Source location in ${view.path}`}
    >
      <div className="source-heading">
        <span>{view.path}</span>
        <span>V0 · read only</span>
      </div>
      <div ref={container} className="monaco-host" hidden={state !== "ready"} />
      {state !== "ready" && (
        <pre
          className="source-fallback"
          aria-label="Highlighted fixture source"
        >
          <code>
            {before}
            <mark>{highlighted}</mark>
            {after}
          </code>
        </pre>
      )}
      {state === "failed" && (
        <p className="editor-warning" role="status">
          Monaco could not load. The verified source and exact highlight remain
          available above.
        </p>
      )}
      <div className="source-footer">
        <span>
          Lines {view.location.start_line}–{view.location.end_line} · columns{" "}
          {view.location.start_column}–{view.location.end_column} (scalar)
        </span>
        <span>End exclusive</span>
      </div>
    </section>
  );
}
