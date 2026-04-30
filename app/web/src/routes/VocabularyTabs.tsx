import { Link, NavLink, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";

function Tabs({ owner, current }: { owner: string; current: "words" | "enums" | "formats" }) {
  const tab = (key: string, label: string) => (
    <li>
      <NavLink to={`/v/${owner}/${key}`} className={current === key ? "active" : ""}>
        {label}
      </NavLink>
    </li>
  );
  return (
    <ul className="nav tabs">
      {tab("words", "Words")}
      {tab("enums", "Enums")}
      {tab("formats", "Formats")}
    </ul>
  );
}

function VocabSidebar({ owner }: { owner: string | undefined }) {
  return (
    <section className="pane">
      <h2>Vocabulary</h2>
      <ul className="nav">
        <li>
          <Link to={`/v/${owner}`}>← profile</Link>
        </li>
      </ul>
      {owner && <Tabs owner={owner} current={"words"} />}
    </section>
  );
}

export function VocabWordsView() {
  const { owner } = useParams();
  const types = useAsync(
    async () => {
      if (!owner) return [];
      const r = await api.GET("/api/types", {
        params: { query: { owner } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [owner],
  );

  return (
    <>
      <VocabSidebar owner={owner} />
      <section className="pane">
        <div className="detail">
          <h1>{owner} — Words</h1>
          <div className="subtitle">All Word Types published by this Vocabulary.</div>
          {owner && (
            <ul className="nav tabs" style={{ marginBottom: 12 }}>
              <li><NavLink to={`/v/${owner}/words`} className="active">Words</NavLink></li>
              <li><NavLink to={`/v/${owner}/enums`}>Enums</NavLink></li>
              <li><NavLink to={`/v/${owner}/formats`}>Formats</NavLink></li>
            </ul>
          )}
          {types.loading && <Loading what="words" />}
          {types.error && <ErrorBox error={types.error} />}
          {types.data && types.data.length === 0 && <Empty what="words" />}
          {types.data && types.data.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>Word</th>
                  <th>Latest</th>
                  <th>Versions</th>
                  <th>Drafts</th>
                  <th>Retired</th>
                </tr>
              </thead>
              <tbody>
                {types.data.map((t) => (
                  <tr key={t.name}>
                    <td>
                      <Link to={`/w/${t.name}`}>{t.name}</Link>
                      {t.is_retired && <StatusPill status="retired" retired />}
                    </td>
                    <td>{t.latest_version && <code>/{t.latest_version}</code>}</td>
                    <td>{t.version_count ?? 0}</td>
                    <td>
                      {t.has_drafts ? (
                        <span className="pill draft">draft {t.draft_version_count}</span>
                      ) : (
                        <span className="meta">—</span>
                      )}
                    </td>
                    <td>{t.is_retired && <span className="pill retired">retired</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export function VocabEnumsView() {
  const { owner } = useParams();
  const enums = useAsync(
    async () => {
      if (!owner) return [];
      const r = await api.GET("/api/enums", {
        params: { query: { owner } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [owner],
  );

  return (
    <>
      <VocabSidebar owner={owner} />
      <section className="pane">
        <div className="detail">
          <h1>{owner} — Enums</h1>
          <div className="subtitle">Versioned controlled vocabularies (Choice sets).</div>
          {owner && (
            <ul className="nav tabs" style={{ marginBottom: 12 }}>
              <li><NavLink to={`/v/${owner}/words`}>Words</NavLink></li>
              <li><NavLink to={`/v/${owner}/enums`} className="active">Enums</NavLink></li>
              <li><NavLink to={`/v/${owner}/formats`}>Formats</NavLink></li>
            </ul>
          )}
          {enums.loading && <Loading what="enums" />}
          {enums.error && <ErrorBox error={enums.error} />}
          {enums.data && enums.data.length === 0 && <Empty what="enums" />}
          {enums.data && enums.data.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>Enum</th>
                  <th>Type</th>
                  <th>Versions</th>
                  <th>Drafts</th>
                  <th>Retired</th>
                </tr>
              </thead>
              <tbody>
                {enums.data.map((e) => (
                  <tr key={e.name}>
                    <td>
                      <Link to={`/enums/${e.name}`}>{e.name}</Link>
                    </td>
                    <td><code>{e.enum_type}</code></td>
                    <td>{e.version_count ?? 0}</td>
                    <td>
                      {e.has_drafts ? (
                        <span className="pill draft">draft {e.draft_version_count}</span>
                      ) : (
                        <span className="meta">—</span>
                      )}
                    </td>
                    <td>{e.is_retired && <span className="pill retired">retired</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export function VocabFormatsView() {
  const { owner } = useParams();
  const formats = useAsync(
    async () => {
      if (!owner) return [];
      const r = await api.GET("/api/formats", {
        params: { query: { owner } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [owner],
  );

  return (
    <>
      <VocabSidebar owner={owner} />
      <section className="pane">
        <div className="detail">
          <h1>{owner} — Formats</h1>
          <div className="subtitle">String-shape constraints (regex + bounds, unversioned).</div>
          {owner && (
            <ul className="nav tabs" style={{ marginBottom: 12 }}>
              <li><NavLink to={`/v/${owner}/words`}>Words</NavLink></li>
              <li><NavLink to={`/v/${owner}/enums`}>Enums</NavLink></li>
              <li><NavLink to={`/v/${owner}/formats`} className="active">Formats</NavLink></li>
            </ul>
          )}
          {formats.loading && <Loading what="formats" />}
          {formats.error && <ErrorBox error={formats.error} />}
          {formats.data && formats.data.length === 0 && <Empty what="formats" />}
          {formats.data && formats.data.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>Format</th>
                  <th>JSON-Schema format</th>
                  <th>Min</th>
                  <th>Max</th>
                  <th>Used by</th>
                  <th>Retired</th>
                </tr>
              </thead>
              <tbody>
                {formats.data.map((f) => (
                  <tr key={f.name}>
                    <td>
                      <Link to={`/formats/${f.name}`}>{f.name}</Link>
                    </td>
                    <td><code>{f.json_schema_format ?? ""}</code></td>
                    <td>{f.min_length ?? ""}</td>
                    <td>{f.max_length ?? ""}</td>
                    <td>{f.total_usage_count ?? 0}</td>
                    <td>{f.is_retired && <span className="pill retired">retired</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}
