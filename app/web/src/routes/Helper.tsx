import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";
import { BoolChip, Chip, ChipRow } from "../components/Chips";
import { RefLink } from "../components/RefLink";

export function HelperView() {
  const { name } = useParams();

  const helper = useAsync(
    async () => {
      if (!name) throw new Error("no name");
      const r = await api.GET("/api/helpers/{name}", { params: { path: { name } } });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [name],
  );

  const attrs = useAsync(
    async () => {
      if (!name) return [];
      const r = await api.GET("/api/helpers/{name}/attributes", {
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
        <h2>Helper</h2>
        {helper.data && (
          <div className="word-summary">
            <div className="word-summary-name">
              <strong>{helper.data.name}</strong>
            </div>
            {helper.data.origin_owner_name && (
              <div className="meta">
                vocab <Link to={`/v/${helper.data.origin_owner_name}`}>{helper.data.origin_owner_name}</Link>
              </div>
            )}
          </div>
        )}
        <h2>Origin</h2>
        {helper.data?.origin_type_version && (
          <ul className="nav">
            <li>
              <Link to={originHref(helper.data.origin_type_version)}>
                ← {helper.data.origin_type_version}
              </Link>
            </li>
          </ul>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {helper.loading && <Loading what="helper" />}
          {helper.error && <ErrorBox error={helper.error} />}
          {helper.data && (
            <>
              <h1>
                {helper.data.name}
                {helper.data.is_origin_draft && <StatusPill status="draft" />}
                {helper.data.origin_word_is_retired && <StatusPill status="retired" retired />}
              </h1>
              <div className="subtitle">
                Originated by{" "}
                {helper.data.origin_type_version && (
                  <Link to={originHref(helper.data.origin_type_version)}>
                    {helper.data.origin_type_version}
                  </Link>
                )}{" "}
                at <code>{helper.data.origin_path}</code>
              </div>
              {helper.data.title && <p><strong>{helper.data.title}</strong></p>}
              {helper.data.description && <p className="description">{helper.data.description}</p>}

              <ChipRow>
                <Chip label="attrs" value={helper.data.attribute_count ?? 0} />
                <Chip label="required" value={helper.data.required_attribute_count ?? 0} />
                <Chip label="used by" value={helper.data.total_usage_count ?? 0} />
                <BoolChip label="closed" value={helper.data.is_closed} trueTone="default" falseTone="warn" />
                <BoolChip label="used" value={helper.data.is_used} trueTone="ok" falseTone="warn" />
              </ChipRow>

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Attributes</h2>
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
                        <td><code>{a.attribute_name}</code></td>
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
            </>
          )}
        </div>
      </section>
    </>
  );
}

function originHref(originTypeVersion: string): string {
  const idx = originTypeVersion.lastIndexOf("/");
  if (idx <= 0) return `/w/${originTypeVersion}`;
  return `/w/${originTypeVersion.slice(0, idx)}/v/${originTypeVersion.slice(idx + 1)}`;
}
