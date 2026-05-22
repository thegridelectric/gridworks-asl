/**
 * RulebookTablesNav — collapsible browser for every rulebook table.
 *
 * Renders one collapsible group per table. Row lists are lazy-fetched the
 * first time a table is expanded (the rulebook has 33 tables and ~2000
 * rows across them; eagerly loading all of them would be wasteful).
 *
 * Big tables (TypeAttributes=967, EnumValues=373, TypeAxioms=161) cap
 * displayed rows at MAX_VISIBLE with a "show all" toggle.
 *
 * Selecting a row tells the parent admin route to render the
 * RulebookEntryForm in the middle pane — same component that's used
 * when a YAML file is selected, just without the surrounding YAML editor.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  adminApi,
  type RulebookSummary,
  type RulebookTableResponse,
  type RulebookTableRow,
} from "../lib/admin";

const MAX_VISIBLE = 50;  // rows shown by default per table; "show all" overrides

export interface RulebookSelection {
  table: string;
  id: string;
}

interface Props {
  summary: RulebookSummary | null;
  selection: RulebookSelection | null;
  onSelect: (sel: RulebookSelection) => void;
}

export function RulebookTablesNav({ summary, selection, onSelect }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showAll, setShowAll] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<Record<string, string>>({});
  // Lazy-loaded row cache per table.
  const [rowsByTable, setRowsByTable] = useState<Record<string, RulebookTableResponse | "loading" | { error: string }>>({});

  // Group tables for readability. Order matters: rulebook-native ones first
  // (the user is most likely to reach for those), YAML-sourced after.
  const groups = useMemo(() => buildGroups(summary), [summary]);

  const toggleExpand = useCallback((table: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(table)) next.delete(table);
      else next.add(table);
      return next;
    });
  }, []);

  // Fetch rows for any newly-expanded table that hasn't been loaded yet.
  useEffect(() => {
    for (const t of expanded) {
      if (rowsByTable[t] !== undefined) continue;
      setRowsByTable((prev) => ({ ...prev, [t]: "loading" }));
      adminApi.listRulebookTable(t)
        .then((resp) => setRowsByTable((prev) => ({ ...prev, [t]: resp })))
        .catch((e) => setRowsByTable((prev) => ({
          ...prev,
          [t]: { error: e instanceof Error ? e.message : String(e) },
        })));
    }
  }, [expanded, rowsByTable]);

  if (!summary) {
    return <div className="rulebook-nav-loading">Loading tables…</div>;
  }

  return (
    <div className="rulebook-nav">
      <h2 className="rulebook-nav-title">Rulebook tables</h2>
      <p className="rulebook-nav-hint">
        Hand-edit any rulebook row. Rows in YAML-sourced tables get overwritten on the next{" "}
        <strong>yaml-to-rulebook</strong> run.
      </p>

      {groups.map(({ label, tables }) => (
        <div key={label} className="rulebook-nav-group">
          <h3 className="rulebook-nav-group-label">{label}</h3>
          {tables.map(([table, rowCount]) => {
            const isExpanded = expanded.has(table);
            const data = rowsByTable[table];
            const isYamlSourced = data && data !== "loading" && !("error" in data) && data.is_yaml_sourced;
            return (
              <div key={table} className={`rulebook-nav-table ${isYamlSourced ? "is-yaml-sourced" : ""}`}>
                <button
                  type="button"
                  className="rulebook-nav-table-head"
                  onClick={() => toggleExpand(table)}
                >
                  <span className="rulebook-nav-arrow">{isExpanded ? "▾" : "▸"}</span>
                  <span className="rulebook-nav-table-name">{table}</span>
                  <span className="rulebook-nav-count">{rowCount}</span>
                </button>
                {isExpanded && (
                  <RulebookRowList
                    table={table}
                    data={data}
                    filter={filter[table] ?? ""}
                    onFilterChange={(v) => setFilter((prev) => ({ ...prev, [table]: v }))}
                    showAll={showAll.has(table)}
                    onToggleShowAll={() => setShowAll((prev) => {
                      const next = new Set(prev);
                      if (next.has(table)) next.delete(table);
                      else next.add(table);
                      return next;
                    })}
                    selection={selection}
                    onSelect={onSelect}
                  />
                )}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function RulebookRowList({
  table,
  data,
  filter,
  onFilterChange,
  showAll,
  onToggleShowAll,
  selection,
  onSelect,
}: {
  table: string;
  data: RulebookTableResponse | "loading" | { error: string } | undefined;
  filter: string;
  onFilterChange: (v: string) => void;
  showAll: boolean;
  onToggleShowAll: () => void;
  selection: RulebookSelection | null;
  onSelect: (sel: RulebookSelection) => void;
}) {
  if (data === undefined || data === "loading") {
    return <div className="rulebook-nav-row-loading">Loading rows…</div>;
  }
  if ("error" in data) {
    return <div className="rulebook-nav-row-error">Error: {data.error}</div>;
  }

  // Filter on id or label, case-insensitive.
  const lcFilter = filter.trim().toLowerCase();
  const matches = lcFilter === ""
    ? data.rows
    : data.rows.filter((r) =>
        r.id.toLowerCase().includes(lcFilter)
        || (r.label?.toLowerCase().includes(lcFilter) ?? false),
      );
  const overCap = matches.length > MAX_VISIBLE;
  const visible = (overCap && !showAll) ? matches.slice(0, MAX_VISIBLE) : matches;

  return (
    <div className="rulebook-nav-rows">
      {data.row_count > 0 && (
        <input
          type="text"
          className="rulebook-nav-filter"
          placeholder={`filter ${data.row_count} rows…`}
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
        />
      )}
      {data.is_yaml_sourced && (
        <div className="rulebook-nav-yaml-warn" title="Editing rows here is fine, but yaml-to-rulebook will overwrite changes on the next build.">
          ⚠ yaml-sourced
        </div>
      )}
      {data.rows.length === 0 && <div className="rulebook-nav-empty">(no rows)</div>}
      {visible.map((row) => (
        <RowItem
          key={row.id}
          table={table}
          row={row}
          isSelected={selection?.table === table && selection?.id === row.id}
          onSelect={() => onSelect({ table, id: row.id })}
        />
      ))}
      {overCap && (
        <button type="button" className="rulebook-nav-show-all" onClick={onToggleShowAll}>
          {showAll
            ? `show first ${MAX_VISIBLE}`
            : `show all ${matches.length} (currently showing ${MAX_VISIBLE})`}
        </button>
      )}
    </div>
  );
}

function RowItem({
  table: _table,
  row,
  isSelected,
  onSelect,
}: {
  table: string;
  row: RulebookTableRow;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`rulebook-nav-row ${isSelected ? "is-selected" : ""}`}
      onClick={onSelect}
      title={row.id}
    >
      <div className="rulebook-nav-row-id">{row.id}</div>
      {row.label && <div className="rulebook-nav-row-label">{row.label}</div>}
    </button>
  );
}

/** Group tables by purpose so the navigator isn't an alphabetical blur. */
function buildGroups(summary: RulebookSummary | null): Array<{ label: string; tables: Array<[string, number]> }> {
  if (!summary) return [];
  const tables = summary.tables;
  const groupMap: Record<string, string[]> = {
    "Schema-of-record (YAML-sourced)": [
      "Owners",
      "Types", "TypeVersions", "TypeAttributes", "TypeAxioms", "TypeExamples",
      "TypeHelpers", "TypeHelperAttributes",
      "Enums", "EnumVersions", "EnumValues",
      "Formats", "FormatExamples",
    ],
    "Upgrades + projections": [
      "Projections", "ProjectionMappings",
      "TypeUpgrades", "TypeUpgradeOps",
      "EnumUpgrades", "EnumUpgradeMappings",
    ],
    "CLI scaffold": ["CliCommands", "CliFlags", "CliExamples"],
    "Snapshot pipeline": ["SeedRequests", "SeedRequestEntries", "Snapshots", "LocalNames", "IndexBuilders", "Templates"],
    "Catalog (Features / Emitters / YAML pointers)": ["YamlFiles", "Emitters", "Features", "FeatureBindings"],
    "App": ["AppUsers"],
  };
  const seen = new Set<string>();
  const out: Array<{ label: string; tables: Array<[string, number]> }> = [];
  for (const [label, ts] of Object.entries(groupMap)) {
    const got: Array<[string, number]> = [];
    for (const t of ts) {
      if (t in tables) {
        got.push([t, tables[t]]);
        seen.add(t);
      }
    }
    if (got.length > 0) out.push({ label, tables: got });
  }
  // Anything not pre-classified goes into a fallback group at the bottom.
  const extras: Array<[string, number]> = [];
  for (const [t, n] of Object.entries(tables)) {
    if (!seen.has(t)) extras.push([t, n]);
  }
  if (extras.length > 0) out.push({ label: "Other", tables: extras });
  return out;
}
