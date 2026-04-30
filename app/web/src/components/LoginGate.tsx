import { useEffect, useState, type ReactNode } from "react";
import {
  AUTH_EVENT,
  clearJwt,
  decodeUntrusted,
  fetchAuthConfig,
  fetchCurrentUser,
  getJwt,
  requestCode,
  setJwt,
  verifyCode,
  type AuthConfig,
  type CurrentUser,
} from "../lib/auth";

type GateState =
  | { kind: "loading" }
  | { kind: "open" }                    // auth not configured upstream — render children
  | { kind: "anonymous"; cfg: AuthConfig }
  | { kind: "authed"; user: CurrentUser };

/**
 * LoginGate
 * ─────────
 * 1. On mount, asks /api/auth/config whether auth is wired (server has
 *    a tenant configured). If not, the gate is "open" and children render.
 * 2. If wired, checks /api/auth/me with whatever JWT is in localStorage.
 *    - 200 → "authed", render children.
 *    - 401 / no JWT → "anonymous", render the two-step login form.
 * 3. Any change to the JWT (login, logout, 401 sweep) refires the check
 *    via the AUTH_EVENT listener.
 */
export function LoginGate({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GateState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function recheck() {
      setState({ kind: "loading" });
      try {
        const cfg = await fetchAuthConfig();
        if (!cfg.configured) {
          if (!cancelled) setState({ kind: "open" });
          return;
        }
        if (!getJwt()) {
          if (!cancelled) setState({ kind: "anonymous", cfg });
          return;
        }
        const user = await fetchCurrentUser();
        if (!cancelled) {
          if (user) setState({ kind: "authed", user });
          else setState({ kind: "anonymous", cfg });
        }
      } catch (err) {
        // Config endpoint unreachable: render a clear failure state
        // rather than a stuck spinner. FAIL-not-FALLBACK.
        if (!cancelled) {
          setState({
            kind: "anonymous",
            cfg: { configured: true, magiclink_base_url: "", tenant_id: null },
          });
          console.error("LoginGate: config check failed", err);
        }
      }
    }

    recheck();
    const handler = () => recheck();
    window.addEventListener(AUTH_EVENT, handler);
    return () => {
      cancelled = true;
      window.removeEventListener(AUTH_EVENT, handler);
    };
  }, []);

  if (state.kind === "loading") {
    return <div style={loadingStyle}>Loading…</div>;
  }
  if (state.kind === "open" || state.kind === "authed") {
    return (
      <>
        {state.kind === "authed" && <SignedInBadge user={state.user} />}
        {children}
      </>
    );
  }
  return <LoginForm cfg={state.cfg} />;
}

function SignedInBadge({ user }: { user: CurrentUser }) {
  return (
    <div style={badgeStyle}>
      <span style={{ color: "var(--fg-muted)" }}>signed in as</span>{" "}
      <strong>{user.email}</strong>
      <button
        type="button"
        onClick={() => clearJwt()}
        style={badgeButtonStyle}
        title="Sign out"
      >
        sign out
      </button>
    </div>
  );
}

function LoginForm({ cfg }: { cfg: AuthConfig }) {
  const [step, setStep] = useState<"email" | "code">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmitEmail(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await requestCode(email.trim());
      setStep("code");
    } catch (err) {
      setError(err instanceof Error ? err.message : "request_failed");
    } finally {
      setBusy(false);
    }
  }

  async function onSubmitCode(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const jwt = await verifyCode(email.trim(), code.trim());
      const claims = decodeUntrusted(jwt);
      if (claims && claims.email && typeof claims.email === "string") {
        // cosmetic only — server is still the trust anchor
      }
      setJwt(jwt);
    } catch (err) {
      setError(err instanceof Error ? err.message : "verify_failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={loginShellStyle}>
      <div style={loginCardStyle}>
        <h1 style={loginTitleStyle}>sema</h1>
        <p style={loginSubtitleStyle}>
          {cfg.tenant_id
            ? "Sign in with a code emailed to you."
            : "Auth is enabled but the tenant is not configured. Contact the admin."}
        </p>

        {step === "email" && (
          <form onSubmit={onSubmitEmail} style={loginFormStyle}>
            <label style={loginLabelStyle} htmlFor="login-email">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              autoComplete="email"
              style={loginInputStyle}
              placeholder="you@example.com"
            />
            <button
              type="submit"
              disabled={busy || !email}
              style={loginButtonStyle}
            >
              {busy ? "Sending…" : "Send code"}
            </button>
          </form>
        )}

        {step === "code" && (
          <form onSubmit={onSubmitCode} style={loginFormStyle}>
            <label style={loginLabelStyle} htmlFor="login-code">
              Code sent to <strong>{email}</strong>
            </label>
            <input
              id="login-code"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              autoFocus
              autoComplete="one-time-code"
              style={loginInputStyle}
              placeholder="6-digit code"
            />
            <button
              type="submit"
              disabled={busy || code.length < 4}
              style={loginButtonStyle}
            >
              {busy ? "Verifying…" : "Sign in"}
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => {
                setStep("email");
                setCode("");
                setError(null);
              }}
              style={loginLinkButtonStyle}
            >
              Use a different email
            </button>
          </form>
        )}

        {error && <div style={errorStyle}>Error: {error}</div>}
      </div>
    </div>
  );
}

const loadingStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  height: "100%",
  color: "var(--fg-muted)",
};

const loginShellStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  height: "100%",
  background: "var(--bg-alt)",
  padding: "24px",
};

const loginCardStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: 360,
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  padding: "24px",
  boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
};

const loginTitleStyle: React.CSSProperties = {
  fontSize: 22,
  fontWeight: 600,
  margin: "0 0 6px",
};

const loginSubtitleStyle: React.CSSProperties = {
  fontSize: 13,
  color: "var(--fg-muted)",
  margin: "0 0 18px",
};

const loginFormStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 8,
};

const loginLabelStyle: React.CSSProperties = {
  fontSize: 12,
  color: "var(--fg-muted)",
};

const loginInputStyle: React.CSSProperties = {
  padding: "8px 10px",
  fontSize: 14,
  border: "1px solid var(--border)",
  borderRadius: 6,
  outline: "none",
  fontFamily: "inherit",
};

const loginButtonStyle: React.CSSProperties = {
  marginTop: 6,
  padding: "9px 12px",
  fontSize: 14,
  fontWeight: 500,
  background: "var(--accent)",
  color: "#fff",
  border: "1px solid var(--accent)",
  borderRadius: 6,
  cursor: "pointer",
};

const loginLinkButtonStyle: React.CSSProperties = {
  marginTop: 4,
  padding: "6px",
  fontSize: 12,
  background: "transparent",
  color: "var(--accent)",
  border: "none",
  cursor: "pointer",
  textAlign: "left",
};

const errorStyle: React.CSSProperties = {
  marginTop: 12,
  padding: "8px 10px",
  fontSize: 12,
  background: "var(--status-retired-bg)",
  color: "var(--status-retired)",
  border: "1px solid var(--status-retired-bg)",
  borderRadius: 6,
};

const badgeStyle: React.CSSProperties = {
  position: "fixed",
  top: 8,
  right: 8,
  padding: "4px 10px",
  fontSize: 11,
  background: "var(--bg-alt)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  zIndex: 1000,
  display: "flex",
  alignItems: "center",
  gap: 8,
};

const badgeButtonStyle: React.CSSProperties = {
  fontSize: 11,
  background: "transparent",
  color: "var(--accent)",
  border: "none",
  cursor: "pointer",
  padding: 0,
};
