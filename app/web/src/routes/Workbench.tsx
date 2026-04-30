import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { components } from "../api/schema";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";

type TypeVersion = components["schemas"]["TypeVersion"];

/**
 * Workbench — APP_PLAN §7. Three stacked panels: Resume / Vocabularies / Activity.
 * Wired against vw_* via the typed FastAPI client.
 */
export function Workbench() {
  const owners = useAsync(
    async () => {
      const r = await api.GET("/api/owners");
      return r.data ?? [];
    },
    [],
  );

  const drafts = useAsync(
    async () => {
      const r = await api.GET("/api/type-versions", {
        params: { query: { status: "draft" } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [],
  );

  const recentTypeVersions = useAsync(
    async () => {
      const r = await api.GET("/api/type-versions");
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [],
  );

  const health = useAsync(
    async () => {
      const r = await api.GET("/api/health");
      return r.data!;
    },
    [],
  );

  const recent = (recentTypeVersions.data ?? [])
    .filter((tv) => !!tv.created)
    .sort((a, b) => (b.created ?? "").localeCompare(a.created ?? ""))
    .slice(0, 10);

  return (
    <>
      <section className="pane">
        <h2>Resume</h2>
        {drafts.loading && <Loading what="drafts" />}
        {drafts.error && <ErrorBox error={drafts.error} />}
        {drafts.data && drafts.data.length === 0 && <Empty what="open drafts" />}
        {drafts.data && drafts.data.length > 0 && (
          <ul className="nav">
            {drafts.data.map((d) => (
              <li key={d.name}>
                <Link to={typeVersionHref(d)}>
                  <span className="meta">draft</span> {d.name}
                </Link>
              </li>
            ))}
          </ul>
        )}
        <h2>Recent activity</h2>
        {recentTypeVersions.loading && <Loading what="activity" />}
        {recent.length === 0 && !recentTypeVersions.loading && <Empty what="recent definitions" />}
        {recent.length > 0 && (
          <ul className="nav">
            {recent.map((tv) => (
              <li key={tv.name}>
                <Link to={typeVersionHref(tv)}>
                  {tv.name} <StatusPill status={tv.status} />
                </Link>
                <div className="meta meta-small" style={{ marginLeft: 18 }}>
                  {tv.created && new Date(tv.created).toLocaleDateString()}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          <h1>Workbench</h1>
          <div className="subtitle">
            {health.data ? (
              <>
                db:{health.data.db ? "ok" : "down"} · rulebook:{health.data.rulebook ? "ok" : "down"}
              </>
            ) : (
              "checking…"
            )}
          </div>

          <h2 style={{ fontSize: 14, marginTop: 16 }}>Vocabularies</h2>
          {owners.loading && <Loading what="owners" />}
          {owners.error && <ErrorBox error={owners.error} />}
          {owners.data && (
            <div className="card-grid">
              {owners.data.map((o) => (
                <Link key={o.owners_id} to={`/v/${o.name}`} className="card">
                  <h3>{o.name}</h3>
                  <div className="meta">
                    types {o.type_count ?? 0} · enums {o.enum_count ?? 0} · formats {o.format_count ?? 0}
                  </div>
                  {o.has_open_drafts && (
                    <div className="meta" style={{ marginTop: 6 }}>
                      <span className="pill draft">{o.draft_type_version_count} draft</span>
                    </div>
                  )}
                </Link>
              ))}
            </div>
          )}

          <h2 style={{ fontSize: 14, marginTop: 24 }}>Open drafts</h2>
          {drafts.data && drafts.data.length === 0 && (
            <div className="placeholder">
              No open drafts. After Phase 1's lifecycle backfill, every existing
              version became <code>active</code>; drafts arrive when something
              gets forked.
            </div>
          )}
          {drafts.data && drafts.data.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>Definition</th>
                  <th>Vocab</th>
                  <th>Attrs</th>
                  <th>Stale refs</th>
                  <th>Promotable</th>
                </tr>
              </thead>
              <tbody>
                {drafts.data.map((d) => (
                  <tr key={d.name}>
                    <td>
                      <Link to={typeVersionHref(d)}>{d.name}</Link>
                      <StatusPill status={d.status} />
                    </td>
                    <td>{d.owner_name && <Link to={`/v/${d.owner_name}`}>{d.owner_name}</Link>}</td>
                    <td>{d.attribute_count ?? 0}</td>
                    <td>
                      {d.has_stale_references ? (
                        <span className="pill warn">{d.stale_reference_count} stale</span>
                      ) : (
                        <span className="meta">—</span>
                      )}
                    </td>
                    <td>
                      {d.is_promotable ? (
                        <span className="pill faint">ready</span>
                      ) : (
                        <span className="meta">no</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {health.data && (
            <details style={{ marginTop: 24 }}>
              <summary style={{ color: "var(--fg-muted)" }}>
                Rulebook tables ({health.data.tables.length})
              </summary>
              <table className="list" style={{ marginTop: 8 }}>
                <thead>
                  <tr>
                    <th>Table</th>
                    <th>Rows</th>
                  </tr>
                </thead>
                <tbody>
                  {health.data.tables.map((t) => (
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

function typeVersionHref(tv: TypeVersion): string {
  return `/w/${tv.type}/v/${tv.version}`;
}
