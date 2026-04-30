import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorBox, Loading, Empty } from "../components/Async";
import type { components } from "../api/schema";

type SearchHit = components["schemas"]["SearchHit"];

const TABLE_LABELS: Record<string, string> = {
  owner: "Vocabularies",
  type: "Words",
  type_version: "Definitions",
  enum: "Enums",
  enum_version: "Enum Versions",
  format: "Formats",
  helper: "Helpers",
  type_axiom: "Axioms",
};

function hrefFor(hit: SearchHit): string | null {
  switch (hit.table) {
    case "owner":
      return `/v/${hit.name}`;
    case "type":
      return `/w/${hit.name}`;
    case "type_version": {
      const idx = hit.name.lastIndexOf("/");
      if (idx <= 0) return null;
      return `/w/${hit.name.slice(0, idx)}/v/${hit.name.slice(idx + 1)}`;
    }
    case "enum":
      return `/enums/${hit.name}`;
    case "enum_version": {
      const idx = hit.name.lastIndexOf("/");
      if (idx <= 0) return null;
      return `/enums/${hit.name.slice(0, idx)}/v/${hit.name.slice(idx + 1)}`;
    }
    case "format":
      return `/formats/${hit.name}`;
    case "helper":
      return `/helpers/${hit.name}`;
    case "type_axiom": {
      // type_axiom name shape: "type/version.axiomN"
      const m = hit.name.match(/^([^/]+)\/([0-9]+)/);
      if (!m) return null;
      return `/w/${m[1]}/v/${m[2]}#axioms`;
    }
    default:
      return null;
  }
}

export function SearchView() {
  const [params, setParams] = useSearchParams();
  const initialQ = params.get("q") ?? "";
  const [q, setQ] = useState(initialQ);
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const queryQ = params.get("q") ?? "";
    if (!queryQ) {
      setHits(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .GET("/api/search", { params: { query: { q: queryQ, limit: 100 } } })
      .then((r) => {
        if (cancelled) return;
        if (r.error) setError(JSON.stringify(r.error));
        else setHits(r.data ?? []);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [params]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setParams(q ? { q } : {});
  };

  const grouped = (hits ?? []).reduce<Record<string, SearchHit[]>>((acc, h) => {
    (acc[h.table] = acc[h.table] || []).push(h);
    return acc;
  }, {});

  return (
    <>
      <section className="pane">
        <h2>Search</h2>
        <div className="meta meta-block">
          Full-text search across<br />
          names, titles, descriptions,<br />
          and axiom statements.
        </div>
        {hits && (
          <>
            <h2>Results by table</h2>
            <ul className="nav">
              {Object.entries(grouped).map(([t, items]) => (
                <li key={t}>
                  <a href={`#tbl-${t}`}>
                    {TABLE_LABELS[t] ?? t} <span className="meta">({items.length})</span>
                  </a>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
      <section className="pane">
        <div className="detail">
          <h1>Search</h1>
          <form onSubmit={submit} className="search-form">
            <input
              type="text"
              placeholder="search names, titles, descriptions, axioms…"
              value={q}
              autoFocus
              onChange={(e) => setQ(e.target.value)}
            />
            <button type="submit">Search</button>
          </form>

          {!params.get("q") && (
            <div className="placeholder">Type a query above. Try: <code>tank</code>, <code>bid</code>, <code>uuid</code>.</div>
          )}
          {loading && <Loading what="results" />}
          {error && <ErrorBox error={error} />}
          {hits && hits.length === 0 && <Empty what="hits" />}
          {hits && hits.length > 0 && (
            <>
              {Object.entries(grouped).map(([t, items]) => (
                <div key={t} id={`tbl-${t}`}>
                  <h2 style={{ marginTop: 24 }}>
                    {TABLE_LABELS[t] ?? t}{" "}
                    <span className="meta">({items.length})</span>
                  </h2>
                  <table className="list">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Title</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((h) => {
                        const href = hrefFor(h);
                        return (
                          <tr key={`${h.table}:${h.id}`}>
                            <td>
                              {href ? <Link to={href}>{h.name}</Link> : <code>{h.name}</code>}
                            </td>
                            <td>{h.title}</td>
                            <td className="cell-description">{h.description}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ))}
            </>
          )}
        </div>
      </section>
    </>
  );
}
