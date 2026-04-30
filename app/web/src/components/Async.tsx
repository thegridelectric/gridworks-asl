import { useEffect, useState } from "react";

export interface AsyncState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

/**
 * Tiny generic loader. Phase 3 keeps state local; if the surface gets bigger
 * we can lift to react-query — until then, simple-and-explicit beats wiring
 * a cache layer.
 */
export function useAsync<T>(
  fn: () => Promise<T>,
  deps: ReadonlyArray<unknown>,
): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let cancelled = false;
    setState({ data: null, error: null, loading: true });
    fn()
      .then((data) => {
        if (!cancelled) setState({ data, error: null, loading: false });
      })
      .catch((e) => {
        if (!cancelled) setState({ data: null, error: String(e), loading: false });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}

export function Loading({ what = "data" }: { what?: string }) {
  return <div className="placeholder">Loading {what}…</div>;
}

export function ErrorBox({ error }: { error: string }) {
  return <div className="placeholder error-box">Error: {error}</div>;
}

export function Empty({ what }: { what: string }) {
  return <div className="placeholder">No {what}.</div>;
}
