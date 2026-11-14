import * as monaco from "monaco-editor/editor/editor.api";
import EditorWorker from "monaco-editor/editor/editor.worker?worker";
import type { SourceView } from "./workspace";

globalThis.MonacoEnvironment = { getWorker: () => new EditorWorker() };

export function createSourceEditor(element: HTMLElement, view: SourceView) {
  monaco.editor.defineTheme("genesis-source", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#142625",
      "editor.foreground": "#d6e4db",
      "editorLineNumber.foreground": "#718d84",
      "editor.selectionBackground": "#395c4c",
    },
  });
  const model = monaco.editor.createModel(view.source, "plaintext");
  const editor = monaco.editor.create(element, {
    model,
    theme: "genesis-source",
    readOnly: true,
    domReadOnly: true,
    ariaLabel: `Read-only fixture source: ${view.path}`,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontFamily: "Consolas, ui-monospace, monospace",
    fontSize: 15,
    lineHeight: 28,
    padding: { top: 22, bottom: 22 },
    renderWhitespace: "all",
    glyphMargin: false,
    lineNumbersMinChars: 3,
    folding: false,
    wordWrap: "on",
    tabSize: 4,
    links: false,
    contextmenu: false,
    hover: { enabled: "off" },
  });
  editor.createDecorationsCollection([
    {
      range: view.range,
      options: {
        inlineClassName: "source-highlight",
        className: "source-line-highlight",
        isWholeLine: false,
      },
    },
  ]);
  editor.setSelection(view.range);
  editor.revealRangeInCenter(view.range);
  return () => {
    editor.dispose();
    model.dispose();
  };
}
