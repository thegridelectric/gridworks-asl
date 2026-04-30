import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading } from "../components/Async";
import { StatusPill } from "../components/StatusPill";
import { BoolChip, Chip, ChipRow } from "../components/Chips";

export function WordView() {
  const { typeName } = useParams();
  const word = useAsync(
    async () => {
      if (!typeName) throw new Error("no typeName");
      const r = await api.GET("/api/types/{name}", { params: { path: { name: typeName } } });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [typeName],
  );

  const versions = useAsync(
    async () => {
      if (!typeName) return [];
      const r = await api.GET("/api/types/{name}/versions", {
        params: { path: { name: typeName } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [typeName],
  );

  return (
    <>
      <section className="pane">
        <h2>Word</h2>
        {word.data && (
          <div className="word-summary">
            <div className="word-summary-name">
              {word.data.is_retired ? (
                <span className="pill retired">{word.data.name}</span>
              ) : (
                <strong>{word.data.name}</strong>
              )}
            </div>
            {word.data.owner && (
              <div className="meta">
                vocab <Link to={`/v/${word.data.owner}`}>{word.data.owner}</Link>
              </div>
            )}
            {word.data.replaced_by && (
              <div className="meta">
                replaced by <Link to={`/w/${word.data.replaced_by}`}>{word.data.replaced_by}</Link>
              </div>
            )}
          </div>
        )}
        <h2>Definitions</h2>
        {versions.loading && <Loading what="versions" />}
        {versions.error && <ErrorBox error={versions.error} />}
        {versions.data && (
          <ul className="nav timeline">
            {versions.data.map((v) => (
              <li key={v.name}>
                <Link to={`/w/${typeName}/v/${v.version}`}>
                  <span className="timeline-version">/{v.version}</span>
                  <StatusPill status={v.status} />
                  {v.is_leaf && <span className="pill leaf">leaf</span>}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {word.loading && <Loading what="word" />}
          {word.error && <ErrorBox error={word.error} />}
          {word.data && (
            <>
              <h1>
                {word.data.name}
                {word.data.is_retired && <StatusPill status="retired" retired />}
              </h1>
              <div className="subtitle">
                {word.data.owner && (
                  <>
                    Vocabulary: <Link to={`/v/${word.data.owner}`}>{word.data.owner}</Link>
                  </>
                )}
              </div>
              {word.data.title && <p>{word.data.title}</p>}
              {word.data.description && <p className="description">{word.data.description}</p>}

              <ChipRow>
                <Chip label="versions" value={word.data.version_count ?? 0} />
                <Chip label="active" value={word.data.active_version_count ?? 0} tone="ok" />
                <Chip label="draft" value={word.data.draft_version_count ?? 0} tone={word.data.has_drafts ? "warn" : "default"} />
                <Chip label="deprecated" value={word.data.deprecated_version_count ?? 0} />
                <BoolChip label="retired" value={word.data.is_retired} trueTone="danger" />
              </ChipRow>

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Version timeline</h2>
              {versions.loading && <Loading what="versions" />}
              {versions.error && <ErrorBox error={versions.error} />}
              {versions.data && versions.data.length === 0 && (
                <div className="placeholder">This Word has no Definitions.</div>
              )}
              {versions.data && versions.data.length > 0 && (
                <table className="list timeline-table">
                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Status</th>
                      <th>Attrs</th>
                      <th>Axioms</th>
                      <th>Examples</th>
                      <th>Helpers</th>
                      <th>Migrations</th>
                      <th>Used as subtype</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.data.map((v) => (
                      <tr key={v.name} className={v.is_leaf ? "is-leaf" : ""}>
                        <td>
                          <Link to={`/w/${typeName}/v/${v.version}`}>/{v.version}</Link>
                          {v.is_root && <span className="pill faint" title="oldest version">root</span>}
                          {v.is_leaf && <span className="pill faint" title="latest version">leaf</span>}
                        </td>
                        <td>
                          <StatusPill status={v.status} retired={v.word_is_retired ?? false} />
                          {v.has_stale_references && (
                            <span className="pill warn" title={`${v.stale_reference_count} stale references`}>
                              stale {v.stale_reference_count}
                            </span>
                          )}
                        </td>
                        <td>{v.attribute_count ?? 0}</td>
                        <td>{v.axiom_count ?? 0}</td>
                        <td>{v.example_count ?? 0}</td>
                        <td>{v.originated_helper_count ?? 0}</td>
                        <td>
                          {v.has_incoming_upgrade && (
                            <span className="arrow" title="incoming upgrade">←</span>
                          )}
                          {v.has_outgoing_upgrade && (
                            <span className="arrow" title="outgoing upgrade">→</span>
                          )}
                          {!v.has_incoming_upgrade && !v.has_outgoing_upgrade && (
                            <span className="meta">—</span>
                          )}
                        </td>
                        <td>{v.total_subtype_usage_count ?? 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          )}
        </div>
      </section>
    </>
  );
}
