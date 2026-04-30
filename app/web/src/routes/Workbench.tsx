import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { components } from "../api/schema";

type Owner = components["schemas"]["Owner"];

export function Workbench() {
  const [owners, setOwners] = useState<Owner[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<components["schemas"]["HealthResponse"] | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const o = await api.GET("/api/owners");
        setOwners(o.data ?? []);
        const h = await api.GET("/api/health");
        if (h.data) setHealth(h.data);
      } catch (e) {
        setError(String(e));
      }
    })();
  }, []);

  return (
    <>
      <section className="pane">
        <h2>Resume</h2>
        <div className="placeholder">Open drafts land in Phase 3.</div>
        <h2>Activity</h2>
        <div className="placeholder">Activity feed lands in Phase 3.</div>
      </section>
      <section className="pane">
        <div className="detail">
          <h1>Workbench</h1>
          <div className="subtitle">
            Phase 2 scaffold · {health ? `db:${health.db ? "ok" : "down"} rulebook:${health.rulebook ? "ok" : "down"}` : "checking…"}
          </div>
          <h2 style={{ fontSize: 14, marginTop: 24 }}>Vocabularies</h2>
          {error && <div className="placeholder">Error loading owners: {error}</div>}
          {owners && (
            <div className="card-grid">
              {owners.map((o) => (
                <Link key={o.owners_id} to={`/v/${o.name}`} className="card">
                  <h3>{o.name}</h3>
                  <div className="meta">
                    types {o.type_count ?? 0} · enums {o.enum_count ?? 0} · formats {o.format_count ?? 0}
                  </div>
                  {o.has_open_drafts && (
                    <div className="meta" style={{ marginTop: 6 }}>
                      <span className="pill draft">drafts open</span>
                    </div>
                  )}
                </Link>
              ))}
            </div>
          )}
          {health && (
            <details style={{ marginTop: 24 }}>
              <summary style={{ color: "var(--fg-muted)" }}>Rulebook tables ({health.tables.length})</summary>
              <table className="list" style={{ marginTop: 8 }}>
                <thead>
                  <tr>
                    <th>Table</th>
                    <th>Rows</th>
                  </tr>
                </thead>
                <tbody>
                  {health.tables.map((t) => (
                    <tr key={t.table}>
                      <td>{t.table}</td>
                      <td>{t.row_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
          )}
        </div>
      </section>
    </>
  );
}
