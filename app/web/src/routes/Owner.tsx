import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { components } from "../api/schema";

type Owner = components["schemas"]["Owner"];

export function OwnerView() {
  const { owner } = useParams();
  const [data, setData] = useState<Owner | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!owner) return;
    void (async () => {
      try {
        const r = await api.GET("/api/owners/{name}", {
          params: { path: { name: owner } },
        });
        if (r.error) setError(JSON.stringify(r.error));
        else setData(r.data ?? null);
      } catch (e) {
        setError(String(e));
      }
    })();
  }, [owner]);

  return (
    <>
      <section className="pane">
        <h2>Vocabulary</h2>
        <ul className="nav">
          <li>
            <Link to={`/v/${owner}/words`}>Words ({data?.type_count ?? "…"})</Link>
          </li>
          <li>
            <Link to={`/v/${owner}/enums`}>Enums ({data?.enum_count ?? "…"})</Link>
          </li>
          <li>
            <Link to={`/v/${owner}/formats`}>Formats ({data?.format_count ?? "…"})</Link>
          </li>
        </ul>
      </section>
      <section className="pane">
        <div className="detail">
          {error && <div className="placeholder">Error: {error}</div>}
          {data && (
            <>
              <h1>{data.name}</h1>
              <div className="subtitle">
                {data.organization || data.owner_type || "—"}
                {data.has_open_drafts && (
                  <>
                    {" · "}
                    <span className="pill draft">drafts open</span>
                  </>
                )}
              </div>
              {data.description && <p>{data.description}</p>}
              <table className="list" style={{ marginTop: 16 }}>
                <tbody>
                  <tr>
                    <th>Words</th>
                    <td>{data.type_count}</td>
                  </tr>
                  <tr>
                    <th>Enums</th>
                    <td>{data.enum_count}</td>
                  </tr>
                  <tr>
                    <th>Formats</th>
                    <td>{data.format_count}</td>
                  </tr>
                  <tr>
                    <th>Active TypeVersions</th>
                    <td>{data.active_type_version_count}</td>
                  </tr>
                  <tr>
                    <th>Draft TypeVersions</th>
                    <td>{data.draft_type_version_count}</td>
                  </tr>
                  <tr>
                    <th>Active EnumVersions</th>
                    <td>{data.active_enum_version_count}</td>
                  </tr>
                  <tr>
                    <th>Draft EnumVersions</th>
                    <td>{data.draft_enum_version_count}</td>
                  </tr>
                </tbody>
              </table>
            </>
          )}
        </div>
      </section>
    </>
  );
}
