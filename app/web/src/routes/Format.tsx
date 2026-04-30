import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAsync, ErrorBox, Loading, Empty } from "../components/Async";
import { StatusPill } from "../components/StatusPill";
import { BoolChip, Chip, ChipRow } from "../components/Chips";

export function FormatView() {
  const { name } = useParams();

  const fmt = useAsync(
    async () => {
      if (!name) throw new Error("no name");
      const r = await api.GET("/api/formats/{name}", { params: { path: { name } } });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data!;
    },
    [name],
  );

  const examples = useAsync(
    async () => {
      if (!name) return [];
      const r = await api.GET("/api/formats/{name}/examples", {
        params: { path: { name } },
      });
      if (r.error) throw new Error(JSON.stringify(r.error));
      return r.data ?? [];
    },
    [name],
  );

  const positives = (examples.data ?? []).filter((e) => !e.is_counter);
  const counters = (examples.data ?? []).filter((e) => !!e.is_counter);

  return (
    <>
      <section className="pane">
        <h2>Format</h2>
        {fmt.data && (
          <div className="word-summary">
            <div className="word-summary-name">
              {fmt.data.is_retired ? (
                <span className="pill retired">{fmt.data.name}</span>
              ) : (
                <strong>{fmt.data.name}</strong>
              )}
            </div>
            {fmt.data.owner && (
              <div className="meta">
                vocab <Link to={`/v/${fmt.data.owner}`}>{fmt.data.owner}</Link>
              </div>
            )}
            {fmt.data.replaced_by && (
              <div className="meta">
                replaced by <Link to={`/formats/${fmt.data.replaced_by}`}>{fmt.data.replaced_by}</Link>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="pane">
        <div className="detail">
          {fmt.loading && <Loading what="format" />}
          {fmt.error && <ErrorBox error={fmt.error} />}
          {fmt.data && (
            <>
              <h1>
                {fmt.data.name}
                {fmt.data.is_retired && <StatusPill status="retired" retired />}
              </h1>
              <div className="subtitle">
                {fmt.data.owner && (
                  <>Vocabulary: <Link to={`/v/${fmt.data.owner}`}>{fmt.data.owner}</Link></>
                )}
              </div>
              {fmt.data.title && <p><strong>{fmt.data.title}</strong></p>}
              {fmt.data.description && <p className="description">{fmt.data.description}</p>}

              <ChipRow>
                {fmt.data.json_schema_format && (
                  <Chip label="format" value={fmt.data.json_schema_format} />
                )}
                {fmt.data.min_length !== null && fmt.data.min_length !== undefined && (
                  <Chip label="minLength" value={fmt.data.min_length} />
                )}
                {fmt.data.max_length !== null && fmt.data.max_length !== undefined && (
                  <Chip label="maxLength" value={fmt.data.max_length} />
                )}
                <Chip label="used by" value={fmt.data.total_usage_count ?? 0} />
                <BoolChip label="retired" value={fmt.data.is_retired} trueTone="danger" />
              </ChipRow>

              {fmt.data.pattern && (
                <>
                  <h2 style={{ fontSize: 14, marginTop: 24 }}>Pattern</h2>
                  <pre className="json-block"><code>{fmt.data.pattern}</code></pre>
                </>
              )}

              <h2 style={{ fontSize: 14, marginTop: 24 }}>Examples</h2>
              {examples.loading && <Loading what="examples" />}
              {examples.error && <ErrorBox error={examples.error} />}
              {examples.data && examples.data.length === 0 && <Empty what="examples" />}
              {(positives.length > 0 || counters.length > 0) && (
                <div className="format-examples">
                  <div>
                    <h3 className="format-examples-h">
                      Positive ({positives.length})
                    </h3>
                    {positives.length === 0 ? (
                      <Empty what="positive examples" />
                    ) : (
                      <ul className="example-list">
                        {positives.map((e) => (
                          <li key={e.name}>
                            <code>{stripQuotes(e.value)}</code>
                            {e.description && <span className="meta"> — {e.description}</span>}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <h3 className="format-examples-h format-examples-h-counter">
                      Counter ({counters.length})
                    </h3>
                    {counters.length === 0 ? (
                      <Empty what="counter examples" />
                    ) : (
                      <ul className="example-list">
                        {counters.map((e) => (
                          <li key={e.name}>
                            <code className="counter">{stripQuotes(e.value)}</code>
                            {e.description && <span className="meta"> — {e.description}</span>}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </>
  );
}

function stripQuotes(s: string | null | undefined): string {
  if (!s) return "";
  // FormatExamples.value comes through wrapped in JSON-encoded quotes.
  if (s.length >= 2 && s.startsWith('"') && s.endsWith('"')) {
    try {
      return JSON.parse(s);
    } catch {
      return s;
    }
  }
  return s;
}
