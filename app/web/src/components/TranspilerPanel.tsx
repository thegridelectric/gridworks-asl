/**
 * TranspilerPanel — invoke remote SSoTme transpilers against the current rulebook.
 *
 * The transpiler catalog comes from a sibling repo
 * (`../api.effortlessapi.com/Versioned-Stable-SSoTme-Tools/tools/effortless/`)
 * — each tool's `ssotme-tool.json` carries its deployed cpln URL. The
 * backend re-reads those files on every list call so we pick up URL
 * rotations without a server restart.
 *
 * Three things this surface is meant to make legible at a glance:
 *  1. The size of the catalog (~31 tools today).
 *  2. Which tools are real implementations vs scaffolds. README still
 *     saying "TODO: Add description" → backend marks `is_scaffold=true`
 *     and we pill it in yellow so users don't expect meaningful output.
 *  3. The round-trip latency. The first POST after a long idle hits a
 *     cpln cold start and can take 60s+; subsequent calls are sub-second.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  adminApi,
  type TranspilerInfo,
  type TranspilerRunResponse,
  type TranspilerRunRequest,
} from "../lib/admin";

type RunState = {
  transpiler: string;
  startedAt: number;
  pending: boolean;
  response?: TranspilerRunResponse;
  error?: string;
};

export function TranspilerPanel() {
  const [catalog, setCatalog] = useState<TranspilerInfo[] | null>(null);
  const [catalogErr, setCatalogErr] = useState<string | null>(null);
  const [catalogDir, setCatalogDir] = useState<string>("");
  const [run, setRun] = useState<RunState | null>(null);
  const [inputKind, setInputKind] = useState<TranspilerRunRequest["input_kind"]>("rulebook");
  const [inputText, setInputText] = useState<string>("");
  const [showScaffolds, setShowScaffolds] = useState(false);

  // Load catalog once on mount.
  useEffect(() => {
    let cancelled = false;
    adminApi.listTranspilers()
      .then((c) => {
        if (cancelled) return;
        setCatalog(c.transpilers);
        setCatalogDir(c.catalog_dir);
        if (!c.catalog_exists) setCatalogErr(`catalog dir not found: ${c.catalog_dir}`);
      })
      .catch((e) => {
        if (cancelled) return;
        setCatalogErr(e instanceof Error ? e.message : String(e));
      });
    return () => { cancelled = true; };
  }, []);

  const visible = useMemo(
    () => (catalog ?? []).filter((t) => showScaffolds || !t.is_scaffold),
    [catalog, showScaffolds],
  );

  const grouped = useMemo(() => {
    const map = new Map<string, TranspilerInfo[]>();
    for (const t of visible) {
      const k = t.category ?? "(uncategorized)";
      if (!map.has(k)) map.set(k, []);
      map.get(k)!.push(t);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [visible]);

  const runTool = useCallback(async (t: TranspilerInfo) => {
    if (run?.pending) return;
    if (!t.url) return;
    const body: TranspilerRunRequest = {
      input_kind: inputKind,
      text: inputKind === "text" ? inputText : undefined,
      timeout_seconds: 90,
    };
    setRun({ transpiler: t.name, startedAt: Date.now(), pending: true });
    try {
      const r = await adminApi.runTranspiler(t.name, body);
      setRun({ transpiler: t.name, startedAt: Date.now(), pending: false, response: r });
    } catch (e) {
      setRun({
        transpiler: t.name,
        startedAt: Date.now(),
        pending: false,
        error: e instanceof Error ? e.message : String(e),
      });
    }
  }, [run, inputKind, inputText]);

  if (catalogErr && !catalog) {
    return (
      <div className="transpiler-panel">
        <h3>Transpilers</h3>
        <div className="admin-error">Catalog error: {catalogErr}</div>
        <div className="tool-runner-hint">Expected sibling repo at <code>{catalogDir}</code>.</div>
      </div>
    );
  }

  return (
    <div className="transpiler-panel">
      <h3>Transpilers (remote)</h3>
      <p className="tool-runner-hint">
        Tools deployed at <code>cpln.app</code>. First call after idle may take 30–90s (cold start).
        Output below appears once the upstream responds.
      </p>

      <div className="transpiler-controls">
        <label className="transpiler-input-kind">
          <span>Send</span>
          <select value={inputKind} onChange={(e) => setInputKind(e.target.value as TranspilerRunRequest["input_kind"])}>
            <option value="rulebook">current rulebook</option>
            <option value="text">custom text</option>
          </select>
        </label>
        <label className="transpiler-show-scaffolds">
          <input type="checkbox" checked={showScaffolds} onChange={(e) => setShowScaffolds(e.target.checked)} />
          <span>Show scaffolds ({(catalog ?? []).filter((t) => t.is_scaffold).length})</span>
        </label>
      </div>

      {inputKind === "text" && (
        <textarea
          className="transpiler-text-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="text to send as cliInputFileContents…"
          rows={3}
        />
      )}

      {!catalog && <p>Loading catalog…</p>}

      {grouped.map(([cat, items]) => (
        <div key={cat} className="transpiler-group">
          <h4 className="transpiler-cat">{cat} <span className="transpiler-count">({items.length})</span></h4>
          {items.map((t) => (
            <TranspilerCard
              key={t.name}
              tool={t}
              running={run?.transpiler === t.name && run.pending}
              onRun={() => runTool(t)}
            />
          ))}
        </div>
      ))}

      {run && <RunResult run={run} />}
    </div>
  );
}

function TranspilerCard({
  tool,
  running,
  onRun,
}: {
  tool: TranspilerInfo;
  running: boolean;
  onRun: () => void;
}) {
  const disabled = running || !tool.url;
  return (
    <div className={`transpiler-card ${tool.is_scaffold ? "is-scaffold" : "is-real"}`}>
      <div className="transpiler-card-head">
        <button type="button" className="tool-run-btn" disabled={disabled} onClick={onRun}>
          {running ? "running…" : "▶"}
        </button>
        <code className="transpiler-name">{tool.name}</code>
        {tool.is_scaffold && <span className="transpiler-pill scaffold" title="README still says 'TODO: Add description'">scaffold</span>}
        {!tool.url && <span className="transpiler-pill no-url">no URL</span>}
        {tool.version && <span className="transpiler-version">{tool.version}</span>}
      </div>
      {tool.description && (
        <div className="transpiler-desc">{tool.description.slice(0, 220)}{tool.description.length > 220 ? "…" : ""}</div>
      )}
      {tool.error && <div className="transpiler-error">⚠ {tool.error}</div>}
    </div>
  );
}

function RunResult({ run }: { run: RunState }) {
  const r = run.response;
  return (
    <div className="transpiler-output">
      <div className="transpiler-output-head">
        <strong>{run.transpiler}</strong>
        {run.pending ? (
          <span className="tool-output-running">streaming…</span>
        ) : run.error ? (
          <span className="tool-output-done" style={{ color: "var(--status-retired)" }}>error</span>
        ) : r ? (
          <span className="tool-output-done">
            upstream {r.status} · {r.elapsed_seconds.toFixed(2)}s
          </span>
        ) : null}
      </div>

      {run.pending && (
        <div className="transpiler-pending">Waiting for upstream… (cpln cold starts can take 30–90s)</div>
      )}
      {run.error && <div className="admin-error">{run.error}</div>}

      {r && r.output_files && r.output_files.length > 0 && (
        <div className="transpiler-files">
          {r.output_files.map((f) => (
            <div key={f.name} className="transpiler-file">
              <div className="transpiler-file-head">
                📄 <code>{f.name}</code>
                <span className="transpiler-file-meta">{f.size_bytes} bytes{f.is_binary ? " (binary)" : ""}</span>
              </div>
              {f.contents !== null && !f.is_binary && (
                <pre className="transpiler-file-body"><code>{f.contents}</code></pre>
              )}
            </div>
          ))}
        </div>
      )}

      {r && r.decode_error && (
        <div className="transpiler-decode-warn">
          Couldn't decode SSoTme FileSet: {r.decode_error}. Raw response below.
        </div>
      )}

      {r && (!r.output_files || r.output_files.length === 0) && (
        <details className="transpiler-raw">
          <summary>Raw response{r.status === 0 ? " (no upstream connection)" : ""}</summary>
          <pre className="tool-output-body">
            {r.response_is_json ? JSON.stringify(r.response, null, 2) : (r.response_text ?? String(r.response))}
          </pre>
        </details>
      )}
    </div>
  );
}
