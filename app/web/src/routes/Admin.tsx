import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { adminApi, type ParityReport, type RulebookSummary, type ToolInfo, type YamlFile } from "../lib/admin";
import { RulebookEntryForm } from "../components/RulebookEntryForm";
import { RulebookTablesNav, type RulebookSelection } from "../components/RulebookTablesNav";
import { TranspilerPanel } from "../components/TranspilerPanel";

/** Either a YAML file on disk OR a rulebook row. The middle pane renders
 *  different content per kind: YAML editor (with optional mirrored-row
 *  form below) vs. rulebook form alone. */
type Selection =
  | { kind: "yaml"; path: string }
  | { kind: "rulebook"; table: string; id: string };

/**
 * /admin — visceral inspector for YAML ↔ rulebook drift.
 *
 * Three columns:
 *   1. ParityScoreboard + YamlTree   (left: state of the world)
 *   2. DiffPane                       (middle: selected file)
 *   3. ToolRunner                     (right: act on it)
 *
 * Design rationale (memory: feedback-ui-demystifies + feedback-app-is-prototype):
 * the parity numbers MUST come from the filesystem and the rulebook JSON,
 * NOT the postgres views. The vw_* layer is downstream of the rulebook, so
 * showing its counts would just echo the rulebook's claim back at you.
 */
export function AdminView() {
  const [parity, setParity] = useState<ParityReport | null>(null);
  const [files, setFiles] = useState<YamlFile[]>([]);
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [summary, setSummary] = useState<RulebookSummary | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloading, setReloading] = useState(false);

  const reload = useCallback(async () => {
    setReloading(true);
    setError(null);
    try {
      const [p, f, t, s] = await Promise.all([
        adminApi.parity(),
        adminApi.listYamlFiles(),
        adminApi.listTools(),
        adminApi.rulebookSummary(),
      ]);
      setParity(p);
      setFiles(f);
      setTools(t.tools);
      setSummary(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setReloading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const selectYaml = useCallback((path: string) => setSelection({ kind: "yaml", path }), []);
  const selectRulebook = useCallback((sel: RulebookSelection) => setSelection({ kind: "rulebook", ...sel }), []);

  const yamlSelected = selection?.kind === "yaml" ? selection.path : null;
  const rulebookSelected = selection?.kind === "rulebook" ? selection : null;

  return (
    <div className="admin-shell">
      <div className="admin-col admin-col-left">
        <ParityScoreboard parity={parity} reloading={reloading} onRefresh={reload} />
        {error && <div className="admin-error">Error: {error}</div>}
        <YamlTree
          files={files}
          parity={parity}
          selected={yamlSelected}
          onSelect={selectYaml}
        />
        <RulebookTablesNav
          summary={summary}
          selection={rulebookSelected}
          onSelect={selectRulebook}
        />
      </div>
      <div className="admin-col admin-col-middle">
        {selection?.kind === "rulebook" ? (
          <RulebookOnlyPane
            table={selection.table}
            id={selection.id}
            onAfterSave={reload}
          />
        ) : (
          <DiffPane
            selectedPath={selection?.kind === "yaml" ? selection.path : null}
            parity={parity}
            onAfterSave={reload}
          />
        )}
      </div>
      <div className="admin-col admin-col-right">
        <RightTabs tools={tools} onAfterRun={reload} />
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */
/* RulebookOnlyPane — middle pane when a rulebook row (no YAML) is selected */
/* ─────────────────────────────────────────────────────────────────────── */

function RulebookOnlyPane({
  table,
  id,
  onAfterSave,
}: {
  table: string;
  id: string;
  onAfterSave: () => void;
}) {
  return (
    <div className="diff-pane">
      <div className="diff-pane-header">
        <code>rulebook · {table}</code>
      </div>
      <RulebookEntryForm table={table} id={id} onAfterSave={onAfterSave} />
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */
/* ParityScoreboard                                                         */
/* ─────────────────────────────────────────────────────────────────────── */

function ParityScoreboard({
  parity,
  reloading,
  onRefresh,
}: {
  parity: ParityReport | null;
  reloading: boolean;
  onRefresh: () => void;
}) {
  if (!parity) {
    return (
      <div className="parity-scoreboard">
        <div className="parity-headline">Loading parity…</div>
      </div>
    );
  }
  const total = parity.yaml_total;
  const pct = total ? Math.round((parity.matched / total) * 100) : 100;
  const tone =
    parity.missing_in_rulebook === 0 && parity.rulebook_only === 0 ? "ok"
    : parity.missing_in_rulebook > 0 ? "danger" : "warn";

  const emittedAgeStr = parity.emitted_age_seconds == null
    ? "—"
    : formatAge(parity.emitted_age_seconds);

  return (
    <div className={`parity-scoreboard tone-${tone}`}>
      <div className="parity-headline">
        <span className="parity-pct">{pct}%</span>
        <span className="parity-fraction">{parity.matched}/{total} YAML files have a rulebook entry</span>
        <button
          type="button"
          className="parity-refresh"
          onClick={onRefresh}
          disabled={reloading}
          title="Re-read parity from disk + rulebook"
        >
          {reloading ? "↻ …" : "↻"}
        </button>
      </div>
      <div className="parity-detail">
        <span className="parity-chip parity-chip-ok">
          <strong>{parity.matched}</strong> match
        </span>
        <span className={`parity-chip ${parity.missing_in_rulebook ? "parity-chip-danger" : "parity-chip-faint"}`}>
          <strong>{parity.missing_in_rulebook}</strong> missing in rulebook
        </span>
        <span className={`parity-chip ${parity.rulebook_only ? "parity-chip-warn" : "parity-chip-faint"}`}>
          <strong>{parity.rulebook_only}</strong> rulebook-only
        </span>
      </div>
      <div className="parity-meta">
        rulebook updated <em>{formatAge(secondsSince(parity.rulebook_mtime))}</em> ago ·{" "}
        {parity.emitted_dir_exists
          ? <>definitions-emitted/ <em>{emittedAgeStr}</em> old</>
          : <span className="parity-warn-text">definitions-emitted/ missing — round-trip-check needs rulebook-to-yaml first</span>}
      </div>
    </div>
  );
}

function secondsSince(unixSeconds: number): number {
  return Math.max(0, Date.now() / 1000 - unixSeconds);
}

function formatAge(sec: number): string {
  if (sec < 60) return `${Math.round(sec)}s`;
  if (sec < 3600) return `${Math.round(sec / 60)}m`;
  if (sec < 86400) return `${Math.round(sec / 3600)}h`;
  return `${Math.round(sec / 86400)}d`;
}

/* ─────────────────────────────────────────────────────────────────────── */
/* YamlTree                                                                 */
/* ─────────────────────────────────────────────────────────────────────── */

function YamlTree({
  files,
  parity,
  selected,
  onSelect,
}: {
  files: YamlFile[];
  parity: ParityReport | null;
  selected: string | null;
  onSelect: (path: string) => void;
}) {
  // Status lookup: composite key matches what parity rows use.
  const statusByKey = useMemo(() => {
    const m = new Map<string, "match" | "missing_in_rulebook" | "rulebook_only">();
    if (!parity) return m;
    for (const r of parity.rows) {
      const k = `${r.kind}/${r.name}/${r.version ?? ""}`;
      m.set(k, r.status);
    }
    return m;
  }, [parity]);

  // Group: kind → name → versions
  const grouped = useMemo(() => {
    const out = new Map<string, Map<string, YamlFile[]>>();
    for (const f of files) {
      if (!["types", "enums", "formats"].includes(f.kind)) continue;
      if (!out.has(f.kind)) out.set(f.kind, new Map());
      const nameMap = out.get(f.kind)!;
      if (!nameMap.has(f.name)) nameMap.set(f.name, []);
      nameMap.get(f.name)!.push(f);
    }
    return out;
  }, [files]);

  // Also surface rulebook-only entries — they have no YAML file but the user
  // should still see them so they can decide to delete from rulebook or add
  // a YAML.
  const rulebookOnly = useMemo(
    () => (parity?.rows ?? []).filter((r) => r.status === "rulebook_only"),
    [parity],
  );

  return (
    <div className="yaml-tree">
      {Array.from(grouped.entries()).map(([kind, names]) => (
        <div key={kind} className="yaml-tree-group">
          <h3 className="yaml-tree-kind">{kind}</h3>
          {Array.from(names.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([name, versions]) => (
              <div key={name} className="yaml-tree-name">
                <div className="yaml-tree-name-label">{name}</div>
                <div className="yaml-tree-versions">
                  {versions.sort((a, b) => (a.version ?? "").localeCompare(b.version ?? "")).map((f) => {
                    const key = `${f.kind}/${f.name}/${f.version ?? ""}`;
                    const status = statusByKey.get(key) ?? "match";
                    const isSelected = selected === f.path;
                    return (
                      <button
                        key={f.path}
                        type="button"
                        className={`yaml-tree-file status-${status} ${isSelected ? "is-selected" : ""}`}
                        onClick={() => onSelect(f.path)}
                        title={`${f.path} (${status})`}
                      >
                        <StatusIcon status={status} />
                        <span className="yaml-tree-version">{f.version ?? "—"}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
        </div>
      ))}

      {rulebookOnly.length > 0 && (
        <div className="yaml-tree-group">
          <h3 className="yaml-tree-kind">rulebook-only (no YAML)</h3>
          {rulebookOnly.map((r) => (
            <div key={`${r.kind}-${r.name}-${r.version}`} className="yaml-tree-rulebook-only">
              <StatusIcon status="rulebook_only" />
              <span>
                {r.kind}/{r.name}/{r.version ?? "—"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusIcon({
  status,
}: {
  status: "match" | "missing_in_rulebook" | "rulebook_only";
}) {
  if (status === "match") return <span className="status-icon ok" title="In rulebook">●</span>;
  if (status === "missing_in_rulebook")
    return <span className="status-icon missing" title="Missing in rulebook">○</span>;
  return <span className="status-icon orphan" title="Rulebook has it, no YAML on disk">⚠</span>;
}

/* ─────────────────────────────────────────────────────────────────────── */
/* DiffPane                                                                 */
/* ─────────────────────────────────────────────────────────────────────── */

/** Loaded state from the server. `body` is what disk had at last GET;
 *  `sha256` is the optimistic-lock token to echo on PUT. */
interface LoadedFile {
  body: string;
  sha256: string;
  mtime: number;
}

function DiffPane({
  selectedPath,
  parity,
  onAfterSave,
}: {
  selectedPath: string | null;
  parity: ParityReport | null;
  onAfterSave: () => void;
}) {
  const [loaded, setLoaded] = useState<LoadedFile | null>(null);
  const [draft, setDraft] = useState<string>("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState<{ expected: string; actual: string } | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  // Re-fetch whenever the selected file changes.
  useEffect(() => {
    if (!selectedPath) {
      setLoaded(null);
      setDraft("");
      setEditing(false);
      setError(null);
      setConflict(null);
      setSavedAt(null);
      return;
    }
    let cancelled = false;
    setError(null);
    setConflict(null);
    setLoaded(null);
    setEditing(false);
    setSavedAt(null);
    adminApi.getYamlFile(selectedPath)
      .then((f) => {
        if (cancelled) return;
        setLoaded({ body: f.body, sha256: f.sha256, mtime: f.mtime });
        setDraft(f.body);
      })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : String(e)); });
    return () => { cancelled = true; };
  }, [selectedPath]);

  // Dirty = draft diverges from what we last fetched. Saving identical
  // content is silly but harmless — disable Save when not dirty.
  const dirty = loaded !== null && draft !== loaded.body;

  const enterEdit = useCallback(() => {
    setEditing(true);
    setError(null);
    setSavedAt(null);
  }, []);

  const cancelEdit = useCallback(() => {
    if (loaded) setDraft(loaded.body);
    setEditing(false);
    setError(null);
    setConflict(null);
  }, [loaded]);

  const reloadFromDisk = useCallback(async () => {
    if (!selectedPath) return;
    setError(null);
    setConflict(null);
    try {
      const f = await adminApi.getYamlFile(selectedPath);
      setLoaded({ body: f.body, sha256: f.sha256, mtime: f.mtime });
      setDraft(f.body);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [selectedPath]);

  const save = useCallback(async () => {
    if (!selectedPath || !loaded || !dirty) return;
    setSaving(true);
    setError(null);
    setConflict(null);
    try {
      const w = await adminApi.putYamlFile(selectedPath, {
        body: draft,
        expected_sha256: loaded.sha256,
      });
      setLoaded({ body: draft, sha256: w.sha256, mtime: w.mtime });
      setSavedAt(Date.now());
      setEditing(false);
      // Parity may shift if e.g. the entry's identifying fields changed.
      onAfterSave();
    } catch (e) {
      const err = e as Error & { detail?: { error?: string; expected?: string; actual?: string; message?: string }; status?: number };
      if (err.status === 409 && err.detail?.error === "sha256_mismatch") {
        setConflict({
          expected: err.detail.expected ?? "?",
          actual: err.detail.actual ?? "?",
        });
      } else if (err.detail?.error === "invalid_yaml") {
        setError(`YAML parse error: ${err.detail.message ?? "(no message)"}`);
      } else {
        setError(err.message);
      }
    } finally {
      setSaving(false);
    }
  }, [selectedPath, loaded, draft, dirty, onAfterSave]);

  if (!selectedPath) {
    return (
      <div className="diff-pane diff-pane-empty">
        <p>Select a YAML file on the left to inspect or edit.</p>
        <p className="diff-pane-empty-hint">
          The icon shows whether the rulebook has the corresponding entry —{" "}
          <span className="status-icon ok">●</span> match,{" "}
          <span className="status-icon missing">○</span> missing in rulebook,{" "}
          <span className="status-icon orphan">⚠</span> rulebook-only (no YAML).
        </p>
        <p className="diff-pane-empty-hint">
          Editing a YAML file writes it back to <code>definitions/</code>. After saving, click <strong>yaml-to-rulebook</strong>{" "}
          to fold the change into the rulebook, then watch the parity scoreboard.
        </p>
      </div>
    );
  }

  const row = parity?.rows.find((r) => r.yaml_path === selectedPath);
  const isRecentlySaved = savedAt !== null && Date.now() - savedAt < 4000;

  return (
    <div className="diff-pane">
      <div className="diff-pane-header">
        <code>{selectedPath}</code>
        {row && (
          <span className={`parity-chip parity-chip-${
            row.status === "match" ? "ok" : row.status === "missing_in_rulebook" ? "danger" : "warn"
          }`}>
            {row.status.replace(/_/g, " ")}
          </span>
        )}
        <span className="diff-pane-spacer" />
        {!editing && loaded !== null && (
          <button type="button" className="diff-pane-btn" onClick={enterEdit}>Edit</button>
        )}
        {editing && (
          <>
            {dirty && <span className="diff-pane-dirty" title="Unsaved changes">●</span>}
            <button
              type="button"
              className="diff-pane-btn diff-pane-btn-primary"
              onClick={save}
              disabled={!dirty || saving}
            >
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              className="diff-pane-btn"
              onClick={cancelEdit}
              disabled={saving}
            >
              {dirty ? "Discard" : "Done"}
            </button>
          </>
        )}
        {isRecentlySaved && <span className="diff-pane-saved">saved ✓</span>}
      </div>

      {conflict && (
        <div className="admin-error">
          <strong>Conflict:</strong> the file on disk changed since you started editing
          (expected <code>{conflict.expected.slice(0, 12)}…</code>, found <code>{conflict.actual.slice(0, 12)}…</code>).
          Your draft is preserved.{" "}
          <button type="button" className="diff-pane-btn" onClick={reloadFromDisk}>
            Reload disk version (discard draft)
          </button>
        </div>
      )}
      {error && <div className="admin-error">Error: {error}</div>}

      {loaded === null && !error && <p>Loading…</p>}

      {loaded !== null && !editing && (
        <pre className="diff-pane-body"><code>{loaded.body}</code></pre>
      )}

      {loaded !== null && editing && (
        <textarea
          className="diff-pane-edit"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          spellCheck={false}
          autoFocus
        />
      )}

      {row && row.in_rulebook && rulebookEntryForRow(row) && (
        <div className="diff-pane-rulebook-section">
          <h3 className="diff-pane-section-h">Mirrored rulebook entry</h3>
          <RulebookEntryForm
            table={rulebookEntryForRow(row)!.table}
            id={rulebookEntryForRow(row)!.id}
            onAfterSave={onAfterSave}
          />
        </div>
      )}
    </div>
  );
}

/** For a parity row whose YAML file is selected, work out which rulebook
 *  table + id holds the mirroring entry. Returns null when the row has no
 *  direct rulebook mirror (e.g. types — the YAML file is per-version, so
 *  the mirror lives in TypeVersions, not Types). */
function rulebookEntryForRow(row: { kind: string; name: string; version: string | null; in_rulebook: boolean }):
  | { table: string; id: string }
  | null {
  if (!row.in_rulebook) return null;
  if (row.kind === "types" && row.version != null) {
    return { table: "TypeVersions", id: `${row.name}/${row.version}` };
  }
  if (row.kind === "enums" && row.version != null) {
    return { table: "EnumVersions", id: `${row.name}/${row.version}` };
  }
  if (row.kind === "formats") {
    return { table: "Formats", id: row.name };
  }
  return null;
}

/* ─────────────────────────────────────────────────────────────────────── */
/* RightTabs — Local tools (subprocess) vs Transpilers (remote cpln)        */
/* ─────────────────────────────────────────────────────────────────────── */

function RightTabs({
  tools,
  onAfterRun,
}: {
  tools: ToolInfo[];
  onAfterRun: () => void;
}) {
  const [tab, setTab] = useState<"local" | "remote">("local");
  return (
    <div className="right-tabs">
      <div className="right-tabs-bar">
        <button
          type="button"
          className={`right-tab ${tab === "local" ? "is-active" : ""}`}
          onClick={() => setTab("local")}
        >
          Local CLI tools
        </button>
        <button
          type="button"
          className={`right-tab ${tab === "remote" ? "is-active" : ""}`}
          onClick={() => setTab("remote")}
        >
          Transpilers (remote)
        </button>
      </div>
      <div className="right-tabs-body">
        {tab === "local" && <ToolRunner tools={tools} onAfterRun={onAfterRun} />}
        {tab === "remote" && <TranspilerPanel />}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────── */
/* ToolRunner                                                               */
/* ─────────────────────────────────────────────────────────────────────── */

function ToolRunner({
  tools,
  onAfterRun,
}: {
  tools: ToolInfo[];
  onAfterRun: () => void;
}) {
  const [running, setRunning] = useState<string | null>(null);
  const [output, setOutput] = useState<{ tool: string; chunks: string[]; done: boolean } | null>(null);
  const outRef = useRef<HTMLPreElement | null>(null);

  // Autoscroll output as new chunks arrive.
  useEffect(() => {
    if (outRef.current) outRef.current.scrollTop = outRef.current.scrollHeight;
  }, [output?.chunks.length]);

  const run = useCallback(async (toolName: string) => {
    if (running) return;
    setRunning(toolName);
    setOutput({ tool: toolName, chunks: [], done: false });
    try {
      const res = await adminApi.runTool(toolName);
      if (!res.ok || !res.body) {
        setOutput((prev) => prev ? { ...prev, chunks: [...prev.chunks, `\n[ERROR] HTTP ${res.status}\n`], done: true } : prev);
        return;
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value, { stream: true });
        setOutput((prev) => prev ? { ...prev, chunks: [...prev.chunks, text] } : prev);
      }
      setOutput((prev) => prev ? { ...prev, done: true } : prev);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setOutput((prev) => prev ? { ...prev, chunks: [...prev.chunks, `\n[ERROR] ${msg}\n`], done: true } : prev);
    } finally {
      setRunning(null);
      // Tools may have mutated rulebook or definitions-emitted/. Refresh.
      onAfterRun();
    }
  }, [running, onAfterRun]);

  return (
    <div className="tool-runner">
      <h3>Tools</h3>
      <p className="tool-runner-hint">
        Each button runs a single CLI. Watch the parity scoreboard on the left after a run.
      </p>
      <ul className="tool-list">
        {tools.map((t) => (
          <li key={t.name} className="tool-item">
            <div className="tool-item-head">
              <button
                type="button"
                className="tool-run-btn"
                disabled={!!running}
                onClick={() => run(t.name)}
              >
                {running === t.name ? "running…" : `▶ ${t.name}`}
              </button>
              {t.writes && <span className="tool-writes">writes <code>{t.writes}</code></span>}
            </div>
            <div className="tool-desc">{t.description}</div>
          </li>
        ))}
      </ul>
      {output && (
        <div className="tool-output">
          <div className="tool-output-head">
            <strong>{output.tool}</strong>
            {output.done ? <span className="tool-output-done">done</span> : <span className="tool-output-running">streaming…</span>}
          </div>
          <pre ref={outRef} className="tool-output-body">{output.chunks.join("")}</pre>
        </div>
      )}
    </div>
  );
}
