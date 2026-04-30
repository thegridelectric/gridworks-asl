import { useParams } from "react-router-dom";

export function Placeholder({ phase, title }: { phase: string; title: string }) {
  const params = useParams();
  return (
    <>
      <section className="pane">
        <h2>List / Timeline</h2>
        <div className="placeholder">
          Pane lands in {phase}. URL params: {JSON.stringify(params)}
        </div>
      </section>
      <section className="pane">
        <div className="detail">
          <h1>{title}</h1>
          <div className="subtitle">
            Placeholder route. URL contract is live (APP_PLAN §8). Body lands in {phase}.
          </div>
          <div className="placeholder">
            <strong>Params:</strong>
            <pre>{JSON.stringify(params, null, 2)}</pre>
          </div>
        </div>
      </section>
    </>
  );
}
