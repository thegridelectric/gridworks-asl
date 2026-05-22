// Admin API client. Matches app/api/routes/admin.py.

export interface YamlFile {
  path: string;
  kind: "types" | "enums" | "formats" | "registry" | "owner" | "other";
  name: string;
  version: string | null;
  sha256: string;
  mtime: number;
}

export interface FileBody {
  path: string;
  body: string;
  sha256: string;
  mtime: number;
}

export interface FileWriteRequest {
  body: string;
  /** Optimistic lock: GET sha256 echoed back. null forces last-writer-wins. */
  expected_sha256: string | null;
}

export interface FileWriteResponse {
  path: string;
  sha256: string;
  mtime: number;
  bytes_written: number;
}

export interface FileWriteError {
  error: "sha256_mismatch" | "invalid_yaml" | string;
  expected?: string;
  actual?: string;
  hint?: string;
  message?: string;
}

export interface RulebookSummary {
  path: string;
  tables: Record<string, number>;
  types: string[];
  type_versions: string[];
  enums: string[];
  enum_versions: string[];
  formats: string[];
  rulebook_mtime: number;
}

export interface ParityRow {
  yaml_path: string;
  kind: "types" | "enums" | "formats";
  name: string;
  version: string | null;
  in_yaml: boolean;
  in_rulebook: boolean;
  rulebook_only: boolean;
  status: "match" | "missing_in_rulebook" | "rulebook_only";
}

export interface ParityReport {
  yaml_total: number;
  rulebook_total: number;
  matched: number;
  missing_in_rulebook: number;
  rulebook_only: number;
  rows: ParityRow[];
  emitted_dir_exists: boolean;
  emitted_mtime: number | null;
  emitted_age_seconds: number | null;
  rulebook_mtime: number;
}

export interface ToolInfo {
  name: string;
  description: string;
  writes: string | null;
  argv: string[];
}

export interface ToolsResponse {
  repo_root: string;
  tools: ToolInfo[];
}

export interface FieldSchema {
  name: string;
  datatype: "string" | "integer" | "boolean" | "datetime" | string;
  /** Editable iff type in {"raw", "relationship"}. Others are server-derived. */
  type: "raw" | "relationship" | "aggregation" | "calculated" | "lookup" | string;
  nullable: boolean;
  /** FK target table when type === "relationship". */
  related_to: string | null;
  description: string | null;
  formula: string | null;
}

export interface RulebookEntry {
  table: string;
  id: string;
  row: Record<string, unknown>;
  row_sha256: string;
  rulebook_sha256: string;
  schema: FieldSchema[];
  /** True iff a YAML file under definitions/ corresponds to this row.
   *  The UI uses this to warn that the edit will be overwritten by the
   *  next yaml-to-rulebook run. */
  has_yaml_mirror: boolean;
}

export interface RulebookTableRow {
  id: string;
  label: string | null;
  preview: Record<string, unknown>;
}

export interface RulebookTableResponse {
  table: string;
  key_fields: string[];
  row_count: number;
  rows: RulebookTableRow[];
  is_yaml_sourced: boolean;
}

export interface RulebookEntryWriteRequest {
  row: Record<string, unknown>;
  expected_row_sha256: string | null;
  expected_rulebook_sha256?: string | null;
}

export interface TranspilerInfo {
  name: string;
  display_name: string;
  description: string | null;
  category: string | null;
  version: string | null;
  url: string | null;
  head_url: string | null;
  is_active: boolean;
  /** True when README.md still has the scaffold TODO line — output won't
   *  be meaningful for these until the implementation lands. */
  is_scaffold: boolean;
  requires_api_key: boolean;
  error: string | null;
}

export interface TranspilerCatalog {
  catalog_dir: string;
  catalog_exists: boolean;
  transpilers: TranspilerInfo[];
}

export interface TranspilerOutputFile {
  name: string;
  contents: string | null;
  is_binary: boolean;
  size_bytes: number;
}

export interface TranspilerRunRequest {
  input_kind: "rulebook" | "yaml-file" | "text";
  text?: string;
  yaml_path?: string;
  use_head?: boolean;
  timeout_seconds?: number;
}

export interface TranspilerRunResponse {
  transpiler: string;
  url: string;
  status: number;
  elapsed_seconds: number;
  response: unknown;
  response_is_json: boolean;
  response_text: string | null;
  output_files: TranspilerOutputFile[] | null;
  decode_error: string | null;
}

export interface RulebookEntryError {
  error:
    | "row_sha256_mismatch"
    | "rulebook_sha256_mismatch"
    | "id_mismatch"
    | "unknown_columns"
    | "row_not_found"
    | "unknown_table"
    | string;
  expected?: string;
  actual?: string;
  url_id?: string;
  submitted_id?: string;
  columns?: string[];
  hint?: string;
}

async function jsonGet<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return (await r.json()) as T;
}

export const adminApi = {
  listYamlFiles: () => jsonGet<YamlFile[]>("/api/admin/yaml/files"),
  getYamlFile: (path: string) =>
    jsonGet<FileBody>(`/api/admin/yaml/file?path=${encodeURIComponent(path)}`),
  rulebookSummary: () => jsonGet<RulebookSummary>("/api/admin/rulebook/summary"),
  parity: () => jsonGet<ParityReport>("/api/admin/parity"),
  listTools: () => jsonGet<ToolsResponse>("/api/admin/tools"),

  // Streaming endpoint. Returns the Response so the caller can read the
  // body as a ReadableStream and append chunks to a <pre> as they arrive.
  runTool: (name: string): Promise<Response> =>
    fetch(`/api/admin/tools/${encodeURIComponent(name)}/run`, { method: "POST" }),

  /** Write a YAML file back to disk. Caller MUST pass expected_sha256 from
   *  the prior GET (or explicit null to force). Throws on non-2xx with a
   *  best-effort FileWriteError payload attached as `.detail`. */
  async putYamlFile(
    path: string,
    body: FileWriteRequest,
  ): Promise<FileWriteResponse> {
    const r = await fetch(`/api/admin/yaml/file?path=${encodeURIComponent(path)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      // FastAPI wraps the detail under .detail; surface that to the caller.
      const text = await r.text();
      let detail: FileWriteError | undefined;
      try {
        const json = JSON.parse(text) as { detail?: FileWriteError | string };
        if (typeof json.detail === "object" && json.detail !== null) {
          detail = json.detail;
        } else if (typeof json.detail === "string") {
          detail = { error: json.detail };
        }
      } catch {
        /* keep undefined */
      }
      const err = new Error(`PUT failed (${r.status}): ${detail?.error ?? text.slice(0, 120)}`) as Error & { detail?: FileWriteError; status?: number };
      err.detail = detail;
      err.status = r.status;
      throw err;
    }
    return (await r.json()) as FileWriteResponse;
  },

  listTranspilers: () => jsonGet<TranspilerCatalog>("/api/admin/transpilers"),

  async runTranspiler(
    name: string,
    body: TranspilerRunRequest,
  ): Promise<TranspilerRunResponse> {
    const r = await fetch(`/api/admin/transpilers/${encodeURIComponent(name)}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`runTranspiler failed (${r.status}): ${text.slice(0, 200)}`);
    }
    return (await r.json()) as TranspilerRunResponse;
  },

  getRulebookEntry: (table: string, id: string) =>
    jsonGet<RulebookEntry>(
      `/api/admin/rulebook/entry?table=${encodeURIComponent(table)}&id=${encodeURIComponent(id)}`,
    ),

  listRulebookTable: (table: string) =>
    jsonGet<RulebookTableResponse>(
      `/api/admin/rulebook/table/${encodeURIComponent(table)}`,
    ),

  async putRulebookEntry(
    table: string,
    id: string,
    body: RulebookEntryWriteRequest,
  ): Promise<RulebookEntry> {
    const r = await fetch(
      `/api/admin/rulebook/entry?table=${encodeURIComponent(table)}&id=${encodeURIComponent(id)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
    );
    if (!r.ok) {
      const text = await r.text();
      let detail: RulebookEntryError | undefined;
      try {
        const json = JSON.parse(text) as { detail?: RulebookEntryError | string };
        if (typeof json.detail === "object" && json.detail !== null) {
          detail = json.detail;
        } else if (typeof json.detail === "string") {
          detail = { error: json.detail };
        }
      } catch {
        /* keep undefined */
      }
      const err = new Error(
        `PUT rulebook entry failed (${r.status}): ${detail?.error ?? text.slice(0, 120)}`,
      ) as Error & { detail?: RulebookEntryError; status?: number };
      err.detail = detail;
      err.status = r.status;
      throw err;
    }
    return (await r.json()) as RulebookEntry;
  },
};
