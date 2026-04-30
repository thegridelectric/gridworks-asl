import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";
import { BoolChip, Chip, ChipRow } from "../components/Chips";
import { RefLink } from "../components/RefLink";

export function TypeVersionView() {
  const { typeName, version } = useParams();

  const tv = useAsync(
    async () => {
      if (!typeName || !version) throw new Error("missing path");
      const r = await api.GET("/api/type-versions/{type_name}/{version}", {
        params: { path: { type_name: typeName, version } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [typeName, version],
  );

  const attrs = useAsync(
    async () => {
      if (!typeName || !version) return [];
      const r = await api.GET(
        "/api/type-versions/{type_name}/{version}/attributes",
        { params: { path: { type_name: typeName, version } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [typeName, version],
  );

  const axioms = useAsync(
    async () => {
      if (!typeName || !version) return [];
      const r = await api.GET(
        "/api/type-versions/{type_name}/{version}/axioms",
        { params: { path: { type_name: typeName, version } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [typeName, version],
  );

  const examples = useAsync(
    async () => {
      if (!typeName || !version) return [];
      const r = await api.GET(
        "/api/type-versions/{type_name}/{version}/examples",
        { params: { path: { type_name: typeName, version } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [typeName, version],
  );

  const allHelpers = useAsync(
    async () => {
      const r = await api.GET("/api/helpers");
      return r.data ?? [];
    },
    [],
  );

  const fullName = `${typeName}/${version}`;
  const helpers = (allHelpers.data ?? []).filter(
    (h) => h.origin_type_version === fullName,
  );

  return (
    <>
      <section className="pane">
        <h2>Word</h2>
        <ul className="nav">
          <li>
            <Link to={`/w/${typeName}`}>← {typeName}</Link>
          </li>
        </ul>
        {tv.data && (
          <>
            <h2>This Definition</h2>
            <div className="meta meta-block">
              <div>
                <strong>{tv.data.name}</strong>
              </div>
              <div>
                <StatusPill status={tv.data.status} retired={tv.data.word_is_retired ?? false} />
              </div>
            </div>
            <h2>Sections</h2>
            <ul className="nav">
              <li><a href="#attributes">Attributes ({tv.data.attribute_count ?? 0})</a></li>
              <li><a href="#axioms">Axioms ({tv.data.axiom_count ?? 0})</a></li>
              <li><a href="#examples">Examples ({tv.data.example_count ?? 0})</a></li>
              <li><a href="#helpers">Helpers ({tv.data.originated_helper_count ?? 0})</a></li>
              <li><a href="#migrations">Migrations</a></li>
            </ul>
          </>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {tv.loading && <Loading what="definition" />}
          {tv.error && <ErrorBox error={tv.error} />}
          {tv.data && (
            <>
              <h1>
                <Link to={`/w/${typeName}`}>{typeName}</Link>
                <span className="meta">/</span>
                {version}
                <StatusPill status={tv.data.status} retired={tv.data.word_is_retired ?? false} />
                {tv.data.has_stale_references && (
                  <span className="pill warn" title={`${tv.data.stale_reference_count} attributes reference retired things`}>
                    stale refs {tv.data.stale_reference_count}
                  </span>
                )}
              </h1>
              <div className="subtitle">
                {tv.data.owner_name && (
                  <>vocab <Link to={`/v/${tv.data.owner_name}`}>{tv.data.owner_name}</Link>{" · "}</>
                )}
                {tv.data.created && new Date(tv.data.created).toLocaleDateString()}
                {tv.data.schema_url && (
                  <>
                    {" · "}
                    <a href={tv.data.schema_url} target="_blank" rel="noopener noreferrer">
                      schema URL
                    </a>
                  </>
                )}
              </div>
              {tv.data.title && tv.data.title !== typeName && <p><strong>{tv.data.title}</strong></p>}
              {tv.data.description && <p className="description">{tv.data.description}</p>}

              <ChipRow>
                <Chip label="attrs" value={tv.data.attribute_count ?? 0} />
                <Chip label="required" value={tv.data.required_attribute_count ?? 0} />
                <Chip label="axioms" value={tv.data.axiom_count ?? 0} />
                <Chip label="examples" value={tv.data.example_count ?? 0} />
                <BoolChip label="closed" value={tv.data.is_closed} trueTone="default" falseTone="warn" title="extra_allowed inverse" />
                <BoolChip label="leaf" value={tv.data.is_leaf} trueTone="ok" />
                <BoolChip label="root" value={tv.data.is_root} />
                <Chip label="used as subtype" value={tv.data.total_subtype_usage_count ?? 0} />
                <Chip label="incoming →" value={tv.data.incoming_upgrade_count ?? 0} />
                <Chip label="outgoing →" value={tv.data.outgoing_upgrade_count ?? 0} />
              </ChipRow>

              <h2 id="attributes">Attributes</h2>
              {attrs.loading && <Loading what="attributes" />}
              {attrs.error && <ErrorBox error={attrs.error} />}
              {attrs.data && attrs.data.length === 0 && <Empty what="attributes" />}
              {attrs.data && attrs.data.length > 0 && (
                <table className="list attribute-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Name</th>
                      <th>References</th>
                      <th>Required</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attrs.data.map((a) => (
                      <tr key={a.name} className={a.ref_is_stale ? "is-stale" : ""}>
                        <td className="meta">{a.idx ?? ""}</td>
                        <td>
                          <code>{a.attribute_name}</code>
                        </td>
                        <td>
                          <RefLink
                            refKind={a.ref_kind}
                            primitiveType={a.primitive_type}
                            formatRef={a.format_ref}
                            enumVersionRef={a.enum_version_ref}
                            subTypeVersionRef={a.sub_type_version_ref}
                            helperRef={a.helper_ref}
                            isList={a.is_list}
                            isStale={a.ref_is_stale}
                          />
                        </td>
                        <td>
                          {a.is_required ? (
                            <span className="pill faint">required</span>
                          ) : a.has_default ? (
                            <span className="meta">opt · default {String(a.default ?? "")}</span>
                          ) : (
                            <span className="meta">optional</span>
                          )}
                        </td>
                        <td className="cell-description">{a.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              <h2 id="axioms">Axioms</h2>
              {axioms.loading && <Loading what="axioms" />}
              {axioms.error && <ErrorBox error={axioms.error} />}
              {axioms.data && axioms.data.length === 0 && <Empty what="axioms" />}
              {axioms.data && axioms.data.length > 0 && (
                <ol className="axiom-list">
                  {axioms.data.map((ax) => (
                    <li key={ax.name}>
                      <span className="meta">{ax.name}</span>
                      <div>{ax.statement}</div>
                    </li>
                  ))}
                </ol>
              )}

              <h2 id="examples">Examples</h2>
              {examples.loading && <Loading what="examples" />}
              {examples.error && <ErrorBox error={examples.error} />}
              {examples.data && examples.data.length === 0 && <Empty what="examples" />}
              {examples.data && examples.data.length > 0 && (
                <div className="example-gallery">
                  {examples.data.map((ex) => (
                    <details key={ex.name} open>
                      <summary>{ex.name}</summary>
                      <pre className="json-block">{tryFormatJson(ex.example_json)}</pre>
                    </details>
                  ))}
                </div>
              )}

              <h2 id="helpers">Originated Helpers</h2>
              {allHelpers.loading && <Loading what="helpers" />}
              {allHelpers.error && <ErrorBox error={allHelpers.error} />}
              {!allHelpers.loading && helpers.length === 0 && (
                <div className="placeholder">No Helpers originated by this Definition.</div>
              )}
              {helpers.length > 0 && (
                <table className="list">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Origin path</th>
                      <th>Attrs</th>
                      <th>Used by</th>
                    </tr>
                  </thead>
                  <tbody>
                    {helpers.map((h) => (
                      <tr key={h.name}>
                        <td>
                          <Link to={`/helpers/${h.name}`}>{h.name}</Link>
                        </td>
                        <td className="meta"><code>{h.origin_path}</code></td>
                        <td>{h.attribute_count ?? 0}</td>
                        <td>{h.total_usage_count ?? 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              <h2 id="migrations">Migrations</h2>
              <MigrationArrows
                typeName={typeName!}
                version={version!}
                hasIncoming={tv.data.has_incoming_upgrade ?? false}
                hasOutgoing={tv.data.has_outgoing_upgrade ?? false}
              />
            </>
          )}
        </div>
      </section>
    </>
  );
}

function tryFormatJson(s: string | null | undefined): string {
  if (!s) return "";
  try {
    return JSON.stringify(JSON.parse(s), null, 2);
  } catch {
    return s;
  }
}

function MigrationArrows({
  typeName,
  version,
  hasIncoming,
  hasOutgoing,
}: {
  typeName: string;
  version: string;
  hasIncoming: boolean;
  hasOutgoing: boolean;
}) {
  if (!hasIncoming && !hasOutgoing) {
    return <div className="placeholder">No migrations touch this Definition.</div>;
  }
  // We can't enumerate other versions cheaply without a list endpoint, but we
  // can link to the upgrade-chain page where they're discoverable.
  return (
    <div className="migration-arrows">
      {hasIncoming && (
        <div>
          ← Incoming migration to <code>{typeName}/{version}</code>{" "}
          <Link to={`/type-upgrades/${typeName}`}>see chain</Link>
        </div>
      )}
      {hasOutgoing && (
        <div>
          → Outgoing migration from <code>{typeName}/{version}</code>{" "}
          <Link to={`/type-upgrades/${typeName}`}>see chain</Link>
        </div>
      )}
    </div>
  );
}
