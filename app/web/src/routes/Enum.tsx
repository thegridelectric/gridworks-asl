import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";
import { BoolChip, Chip, ChipRow } from "../components/Chips";

export function EnumView() {
  const { name } = useParams();

  const en = useAsync(
    async () => {
      if (!name) throw new Error("no name");
      const r = await api.GET("/api/enums/{name}", { params: { path: { name } } });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [name],
  );

  const versions = useAsync(
    async () => {
      if (!name) return [];
      const r = await api.GET("/api/enums/{name}/versions", {
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
        <h2>Enum</h2>
        {en.data && (
          <div className="word-summary">
            <div className="word-summary-name">
              {en.data.is_retired ? (
                <span className="pill retired">{en.data.name}</span>
              ) : (
                <strong>{en.data.name}</strong>
              )}
            </div>
            {en.data.owner && (
              <div className="meta">
                vocab <Link to={`/v/${en.data.owner}`}>{en.data.owner}</Link>
              </div>
            )}
            {en.data.replaced_by && (
              <div className="meta">
                replaced by <Link to={`/enums/${en.data.replaced_by}`}>{en.data.replaced_by}</Link>
              </div>
            )}
          </div>
        )}
        <h2>Versions</h2>
        {versions.loading && <Loading what="versions" />}
        {versions.error && <ErrorBox error={versions.error} />}
        {versions.data && (
          <ul className="nav timeline">
            {versions.data.map((v) => (
              <li key={v.name}>
                <Link to={`/enums/${name}/v/${v.version}`}>
                  <span className="timeline-version">/{v.version}</span>
                  <StatusPill status={v.status} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {en.loading && <Loading what="enum" />}
          {en.error && <ErrorBox error={en.error} />}
          {en.data && (
            <>
              <h1>
                {en.data.name}
                {en.data.is_retired && <StatusPill status="retired" retired />}
              </h1>
              <div className="subtitle">
                {en.data.owner && (
                  <>
                    Vocabulary: <Link to={`/v/${en.data.owner}`}>{en.data.owner}</Link>
                  </>
                )}
                {en.data.enum_type && <> · type <code>{en.data.enum_type}</code></>}
              </div>
              {en.data.title && <p><strong>{en.data.title}</strong></p>}
              {en.data.description && <p className="description">{en.data.description}</p>}

              <ChipRow>
                <Chip label="versions" value={en.data.version_count ?? 0} />
                <Chip label="active" value={en.data.active_version_count ?? 0} tone="ok" />
                <Chip label="draft" value={en.data.draft_version_count ?? 0} tone={en.data.has_drafts ? "warn" : "default"} />
                <Chip label="deprecated" value={en.data.deprecated_version_count ?? 0} />
                <BoolChip label="retired" value={en.data.is_retired} trueTone="danger" />
                <BoolChip label="versioned" value={en.data.is_versioned} />
              </ChipRow>

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Version timeline</h2>
              {versions.loading && <Loading what="versions" />}
              {versions.error && <ErrorBox error={versions.error} />}
              {versions.data && versions.data.length === 0 && <Empty what="versions" />}
              {versions.data && versions.data.length > 0 && (
                <table className="list">
                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Status</th>
                      <th>Default</th>
                      <th>Values</th>
                      <th>Used by attrs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.data.map((v) => (
                      <tr key={v.name}>
                        <td>
                          <Link to={`/enums/${name}/v/${v.version}`}>/{v.version}</Link>
                        </td>
                        <td>
                          <StatusPill status={v.status} retired={v.word_is_retired ?? false} />
                        </td>
                        <td>{v.default_symbol && <code>{v.default_symbol}</code>}</td>
                        <td>{v.value_count ?? 0}</td>
                        <td>{v.total_attribute_usage_count ?? 0}</td>
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

export function EnumVersionView() {
  const { name, version } = useParams();

  const ev = useAsync(
    async () => {
      if (!name || !version) throw new Error("missing path");
      const r = await api.GET("/api/enum-versions/{enum_name}/{version}", {
        params: { path: { enum_name: name, version } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [name, version],
  );

  const values = useAsync(
    async () => {
      if (!name || !version) return [];
      const r = await api.GET(
        "/api/enum-versions/{enum_name}/{version}/values",
        { params: { path: { enum_name: name, version } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [name, version],
  );

  return (
    <>
      <section className="pane">
        <h2>Enum</h2>
        <ul className="nav">
          <li>
            <Link to={`/enums/${name}`}>← {name}</Link>
          </li>
        </ul>
        {ev.data && (
          <>
            <h2>This Version</h2>
            <div className="meta meta-block">
              <div><strong>{ev.data.name}</strong></div>
              <div>
                <StatusPill status={ev.data.status} retired={ev.data.word_is_retired ?? false} />
              </div>
            </div>
          </>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {ev.loading && <Loading what="enum version" />}
          {ev.error && <ErrorBox error={ev.error} />}
          {ev.data && (
            <>
              <h1>
                <Link to={`/enums/${name}`}>{name}</Link>
                <span className="meta">/</span>
                {version}
                <StatusPill status={ev.data.status} retired={ev.data.word_is_retired ?? false} />
              </h1>
              <div className="subtitle">
                {ev.data.owner_name && (
                  <>vocab <Link to={`/v/${ev.data.owner_name}`}>{ev.data.owner_name}</Link>{" · "}</>
                )}
                {ev.data.created && new Date(ev.data.created).toLocaleDateString()}
                {ev.data.schema_url && (
                  <>
                    {" · "}
                    <a href={ev.data.schema_url} target="_blank" rel="noopener noreferrer">
                      schema URL
                    </a>
                  </>
                )}
              </div>
              {ev.data.title && <p><strong>{ev.data.title}</strong></p>}
              {ev.data.description && <p className="description">{ev.data.description}</p>}

              <ChipRow>
                <Chip label="values" value={ev.data.value_count ?? 0} />
                <Chip label="default" value={ev.data.default_symbol ?? "—"} />
                <Chip label="used by attrs" value={ev.data.total_attribute_usage_count ?? 0} />
                <BoolChip label="active" value={ev.data.is_active} trueTone="ok" />
                <BoolChip label="draft" value={ev.data.is_draft} trueTone="warn" />
                <BoolChip label="deprecated" value={ev.data.is_deprecated} trueTone="default" />
              </ChipRow>

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Symbols</h2>
              {values.loading && <Loading what="values" />}
              {values.error && <ErrorBox error={values.error} />}
              {values.data && values.data.length === 0 && <Empty what="symbols" />}
              {values.data && values.data.length > 0 && (
                <table className="list">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Symbol</th>
                      <th>Default</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {values.data.map((v) => (
                      <tr key={v.name}>
                        <td className="meta">{v.idx ?? ""}</td>
                        <td><code>{v.symbol ?? v.name}</code></td>
                        <td>{v.is_default && <span className="pill faint">default</span>}</td>
                        <td className="cell-description">{v.description}</td>
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
