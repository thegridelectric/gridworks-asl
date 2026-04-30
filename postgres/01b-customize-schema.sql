-- ============================================================================
-- 01b-customize-schema.sql — sema customizations applied AFTER 01-create-tables
-- ============================================================================
-- Hand-edited (sema has no Airtable / no ERBCustomizations table).
-- Re-applied on every init-db.sh, idempotent. The objects below carry
-- *no* rulebook-managed data, so it is safe to drop/recreate them on
-- every localhost rebuild.
--
-- Contents:
--   1. auth.trusted_tenants  — registry of magic-links tenants this DB honors.
--   2. app.jwt_claims()      — verified JWT claims for the current request.
--   3. app.jwt_email()       — convenience extractor.
--   4. app.jwt_tenant_id()   — convenience extractor.
--
-- The app middleware verifies the JWT in process, then sets a session-LOCAL
-- GUC named "app.jwt_claims" carrying the full claims as JSON. SQL helpers
-- read the GUC. RLS policies (in 04b-customize-policies.sql, future) call
-- app.jwt_email() to filter rows.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS app;

-- ----------------------------------------------------------------------------
-- 1. auth.trusted_tenants
-- ----------------------------------------------------------------------------
-- One row per magic-links tenant whose JWTs this database accepts. The app
-- middleware peeks at the JWT's `tenant_id` claim, looks the row up, and
-- RS256-verifies against `public_key_pem`. is_active=false revokes a tenant
-- without deleting its history.
CREATE TABLE IF NOT EXISTS auth.trusted_tenants (
    tenant_id      TEXT PRIMARY KEY,
    public_key_pem TEXT NOT NULL,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    label          TEXT,
    added_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The anon role (created by bases' privilege template) MUST NOT read this
-- table — public keys aren't secret, but ability to *enumerate trusted
-- issuers* is something we keep behind the admin role.
REVOKE ALL ON auth.trusted_tenants FROM PUBLIC;

-- ----------------------------------------------------------------------------
-- 2-4. app.jwt_*() helpers
-- ----------------------------------------------------------------------------
-- All helpers are STABLE and read the per-transaction GUC `app.jwt_claims`
-- which the app middleware sets via SET LOCAL on each request.
--
-- current_setting(..., true) returns NULL when the GUC is unset, which means
-- "no authenticated user" — RLS policies that key off jwt_email() will then
-- naturally fail closed.
--
-- SECURITY DEFINER + `SET row_security = off` is used on jwt_*() so that
-- helpers invoked from inside an RLS USING/WITH CHECK don't recurse into
-- the very policies they're evaluating (the pattern called out in the
-- magic-links skill, "Gotcha: recursion when the role resolver reads an
-- RLS-protected table"). Helpers here only read the GUC, not tables, so
-- recursion isn't possible — but we keep the pattern for any future helper
-- that does table lookups (e.g. app.jwt_role()).

CREATE OR REPLACE FUNCTION app.jwt_claims()
RETURNS jsonb
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    raw text;
BEGIN
    raw := current_setting('app.jwt_claims', true);
    IF raw IS NULL OR raw = '' THEN
        RETURN NULL;
    END IF;
    RETURN raw::jsonb;
EXCEPTION WHEN others THEN
    RETURN NULL;
END
$$;

CREATE OR REPLACE FUNCTION app.jwt_email()
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT lower(app.jwt_claims() ->> 'email')
$$;

CREATE OR REPLACE FUNCTION app.jwt_tenant_id()
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT app.jwt_claims() ->> 'tenant_id'
$$;

-- Helpers are safe for the anon role to execute (they only read the GUC
-- the middleware itself populated).
GRANT USAGE ON SCHEMA app TO PUBLIC;
GRANT EXECUTE ON FUNCTION app.jwt_claims()    TO PUBLIC;
GRANT EXECUTE ON FUNCTION app.jwt_email()     TO PUBLIC;
GRANT EXECUTE ON FUNCTION app.jwt_tenant_id() TO PUBLIC;
