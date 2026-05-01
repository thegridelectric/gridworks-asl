-- ============================================================================
-- 01b-customize-schema.sql — sema customizations applied AFTER 01-create-tables
-- ============================================================================
-- Hand-edited (sema has no Airtable / no ERBCustomizations table).
-- Re-applied on every init-db.sh, idempotent.
--
-- Single purpose: install a local mirror of the `auth.trusted_tenants` table
-- that bases.effortlessapi.com installs in every Magic-Links-enabled base.
-- Schema matches bases EXACTLY:
--
--     auth.trusted_tenants (tenant_id text PK, public_key_pem text NOT NULL,
--                           created_at timestamptz default now())
--
-- The FastAPI middleware (app/api/auth.py) looks up `public_key_pem` by
-- `tenant_id` and verifies the JWT signature in process. There is no RLS
-- in sema today, so we don't install bases' auth.set_jwt() / auth.email()
-- helpers locally — bases owns those in prod and we'll mirror them only
-- if/when sema adds row-secured tables.
-- ============================================================================

-- Localhost-only: clean-slate the auth.trusted_tenants table so prior
-- shapes (e.g. an earlier draft with is_active/label) get reset to the
-- bases-canonical shape on every init-db.sh run. In prod, bases owns
-- this table and our admin role can't drop it; the IF EXISTS guards
-- keep the failure quiet there. (init-db.sh against prod is a one-time
-- bootstrap event anyway — see DEPLOY.md §0.)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
                WHERE table_schema='auth' AND table_name='trusted_tenants') THEN
        BEGIN
            DROP TABLE auth.trusted_tenants;
        EXCEPTION WHEN insufficient_privilege THEN
            -- bases owns the table in prod; leave it alone.
            RAISE NOTICE 'auth.trusted_tenants exists but is not ours; skipping recreate';
        END;
    END IF;
END $$;

-- Drop the now-unused `app` schema if a previous draft created it.
DROP SCHEMA IF EXISTS app CASCADE;

CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.trusted_tenants (
    tenant_id      TEXT PRIMARY KEY,
    public_key_pem TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

REVOKE ALL ON auth.trusted_tenants FROM PUBLIC;
