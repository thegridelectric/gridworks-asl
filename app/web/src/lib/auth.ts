// Magic-links JWT plumbing for the SPA.
//
// - The JWT is held in localStorage under STORAGE_KEY.
// - A one-time fetch interceptor decorates every same-origin /api/* call
//   with Authorization: Bearer <jwt> when one is present.
// - 401 responses to authenticated calls clear the JWT and broadcast an
//   AUTH_EVENT so the LoginGate can flip back to the login form.
//
// We intentionally do NOT decode the JWT client-side for any
// security-relevant decision — the server is the only trust anchor.
// Decoded payload is read solely for cosmetic things (display the
// signed-in email) and is treated as untrusted otherwise.

const STORAGE_KEY = "sema.auth.jwt.v1";
const DEV_SKIP_KEY = "sema.auth.dev_skip.v1";
export const AUTH_EVENT = "sema:auth-changed";

export function getJwt(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return v && v.length > 0 ? v : null;
  } catch {
    return null;
  }
}

export function setJwt(jwt: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, jwt);
  } catch {
    // localStorage may be unavailable in some embedded contexts; surface
    // failure rather than pretending we stored it.
    throw new Error("could_not_persist_jwt");
  }
  window.dispatchEvent(new CustomEvent(AUTH_EVENT));
}

export function clearJwt(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
  window.dispatchEvent(new CustomEvent(AUTH_EVENT));
}

// Dev-only bypass: when set, LoginGate treats the session as an anonymous
// localhost admin and skips the magic-links round-trip entirely. Server
// routes don't enforce auth today, so this is purely a UI gate flip.
export function getDevSkip(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return localStorage.getItem(DEV_SKIP_KEY) === "1";
  } catch {
    return false;
  }
}

export function setDevSkip(on: boolean): void {
  try {
    if (on) localStorage.setItem(DEV_SKIP_KEY, "1");
    else localStorage.removeItem(DEV_SKIP_KEY);
  } catch {
    /* ignore */
  }
  window.dispatchEvent(new CustomEvent(AUTH_EVENT));
}

export function decodeUntrusted(jwt: string | null): Record<string, unknown> | null {
  if (!jwt) return null;
  const parts = jwt.split(".");
  if (parts.length !== 3) return null;
  try {
    const json = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as Record<string, unknown>;
  } catch {
    return null;
  }
}

let installed = false;

export function installAuthFetchInterceptor(): void {
  if (installed) return;
  installed = true;
  const origFetch = window.fetch.bind(window);

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url =
      typeof input === "string"
        ? input
        : input instanceof URL
          ? input.toString()
          : input.url;
    const isApi = url.startsWith("/api/") || url.includes("://") === false && url.startsWith("api/");

    if (!isApi) return origFetch(input, init);

    const jwt = getJwt();
    const headers = new Headers(
      init?.headers ?? (input instanceof Request ? input.headers : undefined),
    );
    if (jwt && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${jwt}`);
    }

    const res = await origFetch(input, { ...(init ?? {}), headers });

    // /api/auth/* endpoints handle 401 themselves (login form shows the
    // error). Everywhere else, a 401 on an authenticated call means the
    // server stopped trusting the token — clear it and let LoginGate
    // re-render.
    if (res.status === 401 && jwt && !url.includes("/api/auth/")) {
      clearJwt();
    }
    return res;
  };
}

export interface AuthConfig {
  configured: boolean;
  magiclink_base_url: string;
  tenant_id: string | null;
}

export interface CurrentUser {
  email: string;
  tenant_id: string;
  iss: string;
  exp: number | null;
  claims: Record<string, unknown>;
}

export async function fetchAuthConfig(): Promise<AuthConfig> {
  const r = await fetch("/api/auth/config");
  if (!r.ok) throw new Error(`auth_config_${r.status}`);
  return (await r.json()) as AuthConfig;
}

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  const r = await fetch("/api/auth/me");
  if (r.status === 401) return null;
  if (!r.ok) throw new Error(`whoami_${r.status}`);
  return (await r.json()) as CurrentUser;
}

export async function requestCode(email: string): Promise<void> {
  const r = await fetch("/api/auth/request-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    throw new Error(body.detail ?? `request_code_${r.status}`);
  }
}

export async function verifyCode(email: string, code: string): Promise<string> {
  const r = await fetch("/api/auth/verify-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, code }),
  });
  const body = await r.json().catch(() => ({}));
  if (!r.ok || !body.jwt) {
    throw new Error(body.detail ?? `verify_code_${r.status}`);
  }
  return body.jwt as string;
}
