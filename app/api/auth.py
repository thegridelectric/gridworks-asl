"""Magic-links auth wiring.

Two routes proxy the magic-links public endpoints (so the browser never
needs the tenant id baked into its bundle), and one dependency verifies
the Bearer JWT against the per-DB ``auth.trusted_tenants`` registry.

Verification is FAIL-not-FALLBACK: any signature problem, missing
issuer, inactive tenant, expired token, or unknown ``tenant_id`` is a
401 — never a 200 with a downgraded session.

The middleware stamps verified claims on ``request.state.jwt_claims``
and exposes a ``CurrentUser`` Pydantic model via the ``current_user``
dependency. RLS plumbing (``SET LOCAL app.jwt_claims`` per query) is
deferred until the first route actually reads from a row-secured table;
the helper functions live in ``postgres/01b-customize-schema.sql`` ready
for that day.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from . import db

log = logging.getLogger(__name__)

MAGICLINK_BASE_URL = os.getenv(
    "MAGICLINK_BASE_URL", "https://magiclink.effortlessapi.com"
).rstrip("/")
MAGICLINK_TENANT_ID = os.getenv("MAGICLINK_TENANT_ID", "").strip()

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class RequestCodeIn(BaseModel):
    email: EmailStr


class RequestCodeOut(BaseModel):
    ok: bool


class VerifyCodeIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)


class VerifyCodeOut(BaseModel):
    ok: bool
    jwt: str
    expires_in: int | None = None


class CurrentUser(BaseModel):
    email: str
    tenant_id: str
    iss: str
    exp: int | None = None
    claims: dict[str, Any]


# ---------------------------------------------------------------------------
# Routes — magic-links proxy
# ---------------------------------------------------------------------------


def _require_tenant_id() -> str:
    if not MAGICLINK_TENANT_ID:
        # FAIL-not-FALLBACK: surfacing this misconfig as a 503 beats
        # silently emailing nothing or signing JWTs for a phantom tenant.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="auth_not_configured: MAGICLINK_TENANT_ID is unset",
        )
    return MAGICLINK_TENANT_ID


@router.post("/request-code", response_model=RequestCodeOut)
async def request_code(payload: RequestCodeIn) -> RequestCodeOut:
    """Forward to ``POST {magiclink}/api/tenants/{tenant_id}/send-code``.

    Magic-links itself returns ``ok: true`` even for emails that don't
    correspond to anything — that's the privacy-preserving design (don't
    leak which addresses exist). We propagate that shape.
    """
    tenant_id = _require_tenant_id()
    url = f"{MAGICLINK_BASE_URL}/api/tenants/{tenant_id}/send-code"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json={"email": payload.email})
    if resp.status_code >= 400:
        log.warning("magic-links send-code failed: %s %s", resp.status_code, resp.text)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="magiclink_unreachable",
        )
    return RequestCodeOut(ok=bool(resp.json().get("ok", True)))


@router.post("/verify-code", response_model=VerifyCodeOut)
async def verify_code(payload: VerifyCodeIn) -> VerifyCodeOut:
    """Forward to ``POST {magiclink}/api/tenants/{tenant_id}/verify-code``.

    On success we return the JWT to the browser. The browser stashes it
    in ``localStorage`` and sends it as ``Authorization: Bearer <jwt>``
    on subsequent calls. We do **not** verify the JWT here on the
    return path — verification happens per-request in ``current_user``
    against ``auth.trusted_tenants``. (Verifying twice would just
    duplicate the work.)
    """
    tenant_id = _require_tenant_id()
    url = f"{MAGICLINK_BASE_URL}/api/tenants/{tenant_id}/verify-code"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            url,
            json={"email": payload.email, "code": payload.code},
        )
    body = resp.json() if resp.content else {}
    if resp.status_code >= 400 or not body.get("ok") or not body.get("jwt"):
        # Magic-links uses 200 + ok:false for bad codes, and 4xx for
        # malformed requests. Either is a 401 to our caller.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=body.get("error", "invalid_code"),
        )
    return VerifyCodeOut(
        ok=True,
        jwt=body["jwt"],
        expires_in=body.get("expires_in"),
    )


# ---------------------------------------------------------------------------
# Dependency — verify Bearer JWT against auth.trusted_tenants
# ---------------------------------------------------------------------------


async def _lookup_public_key(tenant_id: str) -> str | None:
    """Look up an active trusted tenant's public key. Returns None if
    no active row exists. Cached briefly per-process via ``functools``
    in a future iteration; for now a fresh query per request keeps
    revocation immediate."""
    row = await db.fetch_one(
        "SELECT public_key_pem FROM auth.trusted_tenants "
        "WHERE tenant_id = %s AND is_active = true",
        tenant_id,
    )
    if row is None:
        return None
    return row["public_key_pem"]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def current_user(
    authorization: str | None = Header(default=None),
) -> CurrentUser:
    """Verify the Bearer JWT and return the claims.

    Steps (per the magic-links skill, "Sharing one tenant across multiple
    databases"):
      1. Peek at the JWT's ``tenant_id`` claim *without* verifying.
      2. Look it up in ``auth.trusted_tenants``.
      3. RS256-verify against that row's ``public_key_pem``, with the
         expected issuer pinned to the JWT's ``iss`` claim.
      4. Return the decoded claims.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("missing_token")
    token = authorization.split(None, 1)[1].strip()

    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except jwt.InvalidTokenError:
        raise _unauthorized("malformed_token")

    tenant_claim = unverified.get("tenant_id")
    iss_claim = unverified.get("iss")
    if not tenant_claim or not iss_claim:
        raise _unauthorized("missing_tenant_or_iss")

    public_key = await _lookup_public_key(tenant_claim)
    if public_key is None:
        # Either unknown or deactivated. Either way, do not honor.
        raise _unauthorized("unknown_or_revoked_tenant")

    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=iss_claim,
            options={"require": ["exp", "iss", "tenant_id", "email"]},
        )
    except jwt.ExpiredSignatureError:
        raise _unauthorized("expired_token")
    except jwt.InvalidTokenError as e:
        log.info("jwt verification failed: %s", e)
        raise _unauthorized("invalid_token")

    # Belt-and-suspenders: tenant_id in the verified payload must match
    # the one we used to look up the key.
    if claims.get("tenant_id") != tenant_claim:
        raise _unauthorized("tenant_mismatch")

    return CurrentUser(
        email=str(claims.get("email", "")).lower(),
        tenant_id=str(claims["tenant_id"]),
        iss=str(claims["iss"]),
        exp=claims.get("exp"),
        claims=claims,
    )


# ---------------------------------------------------------------------------
# /api/auth/me — proves the round-trip works
# ---------------------------------------------------------------------------


@router.get("/me", response_model=CurrentUser)
async def whoami(user: CurrentUser = Depends(current_user)) -> CurrentUser:
    return user


@router.get("/config")
async def auth_config() -> dict[str, Any]:
    """Public, unauthenticated. Lets the SPA know if auth is wired."""
    return {
        "configured": bool(MAGICLINK_TENANT_ID),
        "magiclink_base_url": MAGICLINK_BASE_URL,
        "tenant_id": MAGICLINK_TENANT_ID or None,
    }


# ---------------------------------------------------------------------------
# Future: per-request DB connection that SET LOCAL app.jwt_claims
# ---------------------------------------------------------------------------
# When the first RLS-protected route lands, swap its db.fetch_* calls for
# a connection-scoped helper like:
#
#     async with db.conn() as c:
#         await c.execute(
#             "SELECT set_config('app.jwt_claims', %s, true)",
#             (json.dumps(user.claims),),
#         )
#         async with c.cursor() as cur:
#             await cur.execute("SELECT * FROM vw_owners")
#             ...
#
# The set_config(..., true) makes the GUC LOCAL — it disappears at txn
# end so it can't leak across requests on a pooled connection.

__all__ = [
    "router",
    "current_user",
    "CurrentUser",
    "MAGICLINK_BASE_URL",
    "MAGICLINK_TENANT_ID",
]
# json import retained for the contextual snippet above; suppress unused warnings.
_ = json
