import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { BoolChip, Chip, ChipRow } from "../components/Chips";

export function ProjectionView() {
  const { name } = useParams();

  const proj = useAsync(
    async () => {
      if (!name) throw new Error("no name");
      const r = await api.GET("/api/projections/{name}", {
        params: { path: { name } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [name],
  );

  const mappings = useAsync(
    async () => {
      if (!name) return [];
      const r = await api.GET("/api/projections/{name}/mappings", {
        params: { path: { name } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [name],
  );

  return (
    <>
      <section className="pane">
        <h2>Projection</h2>
        {proj.data && (
          <>
            <div className="word-summary">
              <div className="word-summary-name">
                <strong>{proj.data.name}</strong>
              </div>
              <div className="meta">
                {proj.data.from_owner_name && (
                  <>vocab <Link to={`/v/${proj.data.from_owner_name}`}>{proj.data.from_owner_name}</Link></>
                )}
              </div>
            </div>
            <h2>Endpoints</h2>
            <ul className="nav">
              {proj.data.from_enum_version && (
                <li>
                  ← from{" "}
                  <Link to={enumVersionHref(proj.data.from_enum_version)}>
                    {proj.data.from_enum_version}
                  </Link>
                </li>
              )}
              {proj.data.to_enum_version && (
                <li>
                  → to{" "}
                  <Link to={enumVersionHref(proj.data.to_enum_version)}>
                    {proj.data.to_enum_version}
                  </Link>
                </li>
              )}
            </ul>
          </>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {proj.loading && <Loading what="projection" />}
          {proj.error && <ErrorBox error={proj.error} />}
          {proj.data && (
            <>
              <h1>{proj.data.name}</h1>
              <div className="subtitle">
                {proj.data.from_enum_version && (
                  <Link to={enumVersionHref(proj.data.from_enum_version)}>
                    {proj.data.from_enum_version}
                  </Link>
                )}
                {" → "}
                {proj.data.to_enum_version && (
                  <Link to={enumVersionHref(proj.data.to_enum_version)}>
                    {proj.data.to_enum_version}
                  </Link>
                )}
              </div>
              {proj.data.description && <p className="description">{proj.data.description}</p>}

              <ChipRow>
                <Chip label="mappings" value={proj.data.mapping_count ?? 0} />
                <BoolChip label="flat lookup" value={proj.data.is_flat_lookup} trueTone="ok" />
                <BoolChip label="scripted" value={proj.data.is_scripted} trueTone="warn" />
                <BoolChip label="cross-enum" value={proj.data.is_cross_enum} />
                <BoolChip label="cross-owner" value={proj.data.is_cross_owner} />
                <Chip label="used in upgrades" value={proj.data.type_upgrade_op_usage_count ?? 0} />
                <BoolChip label="endpoint draft" value={proj.data.has_draft_endpoints} trueTone="warn" />
              </ChipRow>

              {proj.data.raw_script && (
                <>
                  <h2 style={{ fontSize: 14, marginTop: 24 }}>Custom script</h2>
                  <pre className="json-block"><code>{proj.data.raw_script}</code></pre>
                </>
              )}

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Mappings</h2>
              {mappings.loading && <Loading what="mappings" />}
              {mappings.error && <ErrorBox error={mappings.error} />}
              {mappings.data && mappings.data.length === 0 && <Empty what="mappings" />}
              {mappings.data && mappings.data.length > 0 && (
                <table className="list">
                  <thead>
                    <tr>
                      <th>From</th>
                      <th></th>
                      <th>To</th>
                      <th>Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mappings.data.map((m) => (
                      <tr key={m.name}>
                        <td><code>{m.from_symbol ?? m.from_value}</code></td>
                        <td className="meta">→</td>
                        <td>
                          {m.is_removal ? (
                            <span className="pill warn">removed</span>
                          ) : (
                            <code>{m.to_symbol ?? m.to_value}</code>
                          )}
                          {m.is_identity && <span className="pill faint" title="from == to">identity</span>}
                        </td>
                        <td className="cell-description">{m.description}</td>
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

function enumVersionHref(slashName: string): string {
  const idx = slashName.lastIndexOf("/");
  if (idx <= 0) return `/enums/${slashName}`;
  return `/enums/${slashName.slice(0, idx)}/v/${slashName.slice(idx + 1)}`;
}
