import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { BoolChip, Chip, ChipRow } from "../components/Chips";

function typeVersionHref(slashName: string | null | undefined): string | null {
  if (!slashName) return null;
  const idx = slashName.lastIndexOf("/");
  if (idx <= 0) return null;
  return `/w/${slashName.slice(0, idx)}/v/${slashName.slice(idx + 1)}`;
}

function enumVersionHref(slashName: string | null | undefined): string | null {
  if (!slashName) return null;
  const idx = slashName.lastIndexOf("/");
  if (idx <= 0) return null;
  return `/enums/${slashName.slice(0, idx)}/v/${slashName.slice(idx + 1)}`;
}

export function TypeUpgradeChainView() {
  const { name } = useParams();

  const upgrades = useAsync(
    async () => {
      const r = await api.GET("/api/type-upgrades");
      return r.data ?? [];
    },
    [],
  );

  const all = upgrades.data ?? [];
  const filtered = name ? all.filter((u) => u.from_word === name || u.to_word === name) : all;

  return (
    <>
      <section className="pane">
        <h2>Type Upgrades</h2>
        {name ? (
          <ul className="nav">
            <li>
              <Link to={`/w/${name}`}>← {name}</Link>
            </li>
            <li>
              <Link to="/type-upgrades">all type upgrades</Link>
            </li>
          </ul>
        ) : (
          <ul className="nav">
            <li><Link to="/enum-upgrades">enum upgrades →</Link></li>
          </ul>
        )}
        <h2>Edges</h2>
        {filtered.length === 0 && <Empty what="upgrades" />}
        <ul className="nav timeline">
          {filtered.map((u) => (
            <li key={u.name}>
              <Link to={`/type-upgrades/${u.from_word}/${u.from_version}-to-${u.to_version}`}>
                {u.from_word}: /{u.from_version} → /{u.to_version}
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="pane">
        <div className="detail">
          <h1>{name ? `${name} — upgrade chain` : "All type upgrades"}</h1>
          {upgrades.loading && <Loading what="upgrades" />}
          {upgrades.error && <ErrorBox error={upgrades.error} />}
          {filtered.length === 0 && !upgrades.loading && <Empty what="upgrades" />}
          {filtered.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>From</th>
                  <th></th>
                  <th>To</th>
                  <th>Ops</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => {
                  const fromHref = typeVersionHref(u.from_type_version);
                  const toHref = typeVersionHref(u.to_type_version);
                  return (
                    <tr key={u.name}>
                      <td>
                        {fromHref ? <Link to={fromHref}>{u.from_type_version}</Link> : u.from_type_version}
                      </td>
                      <td className="meta">→</td>
                      <td>
                        {toHref ? <Link to={toHref}>{u.to_type_version}</Link> : u.to_type_version}
                      </td>
                      <td>
                        <Link to={`/type-upgrades/${u.from_word}/${u.from_version}-to-${u.to_version}`}>
                          {u.op_count ?? 0} {u.is_scripted ? "· scripted" : ""}
                        </Link>
                      </td>
                      <td className="cell-description">{u.description}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export function TypeUpgradeEdgeView() {
  const { word, fromVersion, toVersion } = useParams();

  const up = useAsync(
    async () => {
      if (!word || !fromVersion || !toVersion) throw new Error("missing path");
      const r = await api.GET(
        "/api/type-upgrades/{word}/{from_version}-to-{to_version}",
        { params: { path: { word, from_version: fromVersion, to_version: toVersion } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [word, fromVersion, toVersion],
  );

  const ops = useAsync(
    async () => {
      if (!word || !fromVersion || !toVersion) return [];
      const r = await api.GET(
        "/api/type-upgrades/{word}/{from_version}-to-{to_version}/ops",
        { params: { path: { word, from_version: fromVersion, to_version: toVersion } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [word, fromVersion, toVersion],
  );

  return (
    <>
      <section className="pane">
        <h2>Type Upgrade</h2>
        <ul className="nav">
          <li>
            <Link to={`/w/${word}`}>← {word}</Link>
          </li>
          <li>
            <Link to={`/type-upgrades/${word}`}>chain</Link>
          </li>
        </ul>
        <h2>Endpoints</h2>
        <ul className="nav">
          <li>
            ← from <Link to={`/w/${word}/v/${fromVersion}`}>{word}/{fromVersion}</Link>
          </li>
          <li>
            → to <Link to={`/w/${word}/v/${toVersion}`}>{word}/{toVersion}</Link>
          </li>
        </ul>
      </section>
      <section className="pane">
        <div className="detail">
          {up.loading && <Loading what="upgrade" />}
          {up.error && <ErrorBox error={up.error} />}
          {up.data && (
            <>
              <h1>
                <Link to={`/w/${word}/v/${fromVersion}`}>{word}/{fromVersion}</Link>
                <span className="meta"> → </span>
                <Link to={`/w/${word}/v/${toVersion}`}>{word}/{toVersion}</Link>
              </h1>
              {up.data.description && <p className="description">{up.data.description}</p>}
              <ChipRow>
                <Chip label="ops" value={up.data.op_count ?? 0} />
                <BoolChip label="decomposed" value={up.data.is_decomposed} trueTone="ok" />
                <BoolChip label="scripted" value={up.data.is_scripted} trueTone="warn" />
                <BoolChip label="cross-word" value={up.data.is_cross_word} trueTone="warn" />
              </ChipRow>

              {up.data.raw_script && (
                <>
                  <h2 style={{ fontSize: 14, marginTop: 24 }}>Whole-method escape hatch</h2>
                  <pre className="json-block"><code>{up.data.raw_script}</code></pre>
                </>
              )}

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Ops</h2>
              {ops.loading && <Loading what="ops" />}
              {ops.error && <ErrorBox error={ops.error} />}
              {ops.data && ops.data.length === 0 && <Empty what="ops" />}
              {ops.data && ops.data.length > 0 && (
                <table className="list">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Kind</th>
                      <th>Field</th>
                      <th>References</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ops.data.map((op) => (
                      <tr key={op.name}>
                        <td className="meta">{op.idx}</td>
                        <td>
                          <code>{op.op_kind}</code>
                          {op.is_custom && <span className="pill warn">custom</span>}
                        </td>
                        <td>{op.field_name && <code>{op.field_name}</code>}</td>
                        <td>
                          {op.enum_version_ref && (
                            <Link to={enumVersionHref(op.enum_version_ref) ?? "#"}>
                              {op.enum_version_ref}
                            </Link>
                          )}
                          {op.projection_ref && (
                            <Link to={`/projections/${op.projection_ref}`}>
                              {op.projection_ref}
                            </Link>
                          )}
                          {op.literal_value && <code className="literal">{op.literal_value}</code>}
                        </td>
                        <td>
                          {op.from_version && <span className="meta">if from /{op.from_version}</span>}
                          {op.to_version && <span className="meta"> → /{op.to_version}</span>}
                          {op.has_raw_script && (
                            <details>
                              <summary>script</summary>
                              <pre className="json-block">{op.raw_script}</pre>
                            </details>
                          )}
                          {op.description && <div className="meta">{op.description}</div>}
                        </td>
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

export function EnumUpgradeChainView() {
  const { name } = useParams();

  const upgrades = useAsync(
    async () => {
      const r = await api.GET("/api/enum-upgrades");
      return r.data ?? [];
    },
    [],
  );

  const all = upgrades.data ?? [];
  const filtered = name ? all.filter((u) => u.from_word === name || u.to_word === name) : all;

  return (
    <>
      <section className="pane">
        <h2>Enum Upgrades</h2>
        {name ? (
          <ul className="nav">
            <li><Link to={`/enums/${name}`}>← {name}</Link></li>
            <li><Link to="/enum-upgrades">all enum upgrades</Link></li>
          </ul>
        ) : (
          <ul className="nav">
            <li><Link to="/type-upgrades">type upgrades →</Link></li>
          </ul>
        )}
        <h2>Edges</h2>
        {filtered.length === 0 && <Empty what="upgrades" />}
        <ul className="nav timeline">
          {filtered.map((u) => (
            <li key={u.name}>
              <Link to={`/enum-upgrades/${u.from_word}/${u.from_version}-to-${u.to_version}`}>
                {u.from_word}: /{u.from_version} → /{u.to_version}
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="pane">
        <div className="detail">
          <h1>{name ? `${name} — upgrade chain` : "All enum upgrades"}</h1>
          {upgrades.loading && <Loading what="upgrades" />}
          {upgrades.error && <ErrorBox error={upgrades.error} />}
          {filtered.length === 0 && !upgrades.loading && <Empty what="upgrades" />}
          {filtered.length > 0 && (
            <table className="list">
              <thead>
                <tr>
                  <th>From</th>
                  <th></th>
                  <th>To</th>
                  <th>Mappings</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => {
                  const fromHref = enumVersionHref(u.from_enum_version);
                  const toHref = enumVersionHref(u.to_enum_version);
                  return (
                    <tr key={u.name}>
                      <td>{fromHref ? <Link to={fromHref}>{u.from_enum_version}</Link> : u.from_enum_version}</td>
                      <td className="meta">→</td>
                      <td>{toHref ? <Link to={toHref}>{u.to_enum_version}</Link> : u.to_enum_version}</td>
                      <td>
                        <Link to={`/enum-upgrades/${u.from_word}/${u.from_version}-to-${u.to_version}`}>
                          {u.mapping_count ?? 0} {u.is_scripted ? "· scripted" : ""}
                        </Link>
                      </td>
                      <td className="cell-description">{u.description}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export function EnumUpgradeEdgeView() {
  const { word, fromVersion, toVersion } = useParams();

  const up = useAsync(
    async () => {
      if (!word || !fromVersion || !toVersion) throw new Error("missing path");
      const r = await api.GET(
        "/api/enum-upgrades/{word}/{from_version}-to-{to_version}",
        { params: { path: { word, from_version: fromVersion, to_version: toVersion } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [word, fromVersion, toVersion],
  );

  const mappings = useAsync(
    async () => {
      if (!word || !fromVersion || !toVersion) return [];
      const r = await api.GET(
        "/api/enum-upgrades/{word}/{from_version}-to-{to_version}/mappings",
        { params: { path: { word, from_version: fromVersion, to_version: toVersion } } },
      );
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [word, fromVersion, toVersion],
  );

  return (
    <>
      <section className="pane">
        <h2>Enum Upgrade</h2>
        <ul className="nav">
          <li><Link to={`/enums/${word}`}>← {word}</Link></li>
          <li><Link to={`/enum-upgrades/${word}`}>chain</Link></li>
        </ul>
        <h2>Endpoints</h2>
        <ul className="nav">
          <li>← from <Link to={`/enums/${word}/v/${fromVersion}`}>{word}/{fromVersion}</Link></li>
          <li>→ to <Link to={`/enums/${word}/v/${toVersion}`}>{word}/{toVersion}</Link></li>
        </ul>
      </section>
      <section className="pane">
        <div className="detail">
          {up.loading && <Loading what="upgrade" />}
          {up.error && <ErrorBox error={up.error} />}
          {up.data && (
            <>
              <h1>
                <Link to={`/enums/${word}/v/${fromVersion}`}>{word}/{fromVersion}</Link>
                <span className="meta"> → </span>
                <Link to={`/enums/${word}/v/${toVersion}`}>{word}/{toVersion}</Link>
              </h1>
              {up.data.description && <p className="description">{up.data.description}</p>}
              <ChipRow>
                <Chip label="mappings" value={up.data.mapping_count ?? 0} />
                <BoolChip label="decomposed" value={up.data.is_decomposed} trueTone="ok" />
                <BoolChip label="scripted" value={up.data.is_scripted} trueTone="warn" />
              </ChipRow>

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Symbol mappings</h2>
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
                          {m.is_identity && <span className="pill faint">identity</span>}
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
