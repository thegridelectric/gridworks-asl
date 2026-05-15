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

-- ============================================================================
-- Vocabulary UPSERT support
-- ============================================================================
-- The YAML SSoT (definitions/) is authoritative for vocabulary. Tool
-- src/sema/tools/sync_vocabulary_to_db.py emits postgres/05c-install-
-- vocabulary.sql which UPSERTs every Word/Version using natural keys.
-- These UNIQUE indexes are what those upserts conflict on; the DEFAULT on
-- *_id columns lets the upserts omit the surrogate PK entirely.
-- All idempotent; safe to re-apply.
-- ============================================================================

-- Surrogate PKs default to a fresh UUID so upserts can omit *_id.
ALTER TABLE owners            ALTER COLUMN owners_id            SET DEFAULT gen_random_uuid()::text;
ALTER TABLE formats           ALTER COLUMN formats_id           SET DEFAULT gen_random_uuid()::text;
ALTER TABLE format_examples   ALTER COLUMN format_examples_id   SET DEFAULT gen_random_uuid()::text;
ALTER TABLE enums             ALTER COLUMN enums_id             SET DEFAULT gen_random_uuid()::text;
ALTER TABLE enum_versions     ALTER COLUMN enum_versions_id     SET DEFAULT gen_random_uuid()::text;
ALTER TABLE enum_values       ALTER COLUMN enum_values_id       SET DEFAULT gen_random_uuid()::text;
ALTER TABLE types             ALTER COLUMN types_id             SET DEFAULT gen_random_uuid()::text;
ALTER TABLE type_versions     ALTER COLUMN type_versions_id     SET DEFAULT gen_random_uuid()::text;
ALTER TABLE type_attributes   ALTER COLUMN type_attributes_id   SET DEFAULT gen_random_uuid()::text;
ALTER TABLE type_examples     ALTER COLUMN type_examples_id     SET DEFAULT gen_random_uuid()::text;
ALTER TABLE type_axioms       ALTER COLUMN type_axioms_id       SET DEFAULT gen_random_uuid()::text;

-- Natural-key UNIQUE indexes (idempotent via IF NOT EXISTS).
CREATE UNIQUE INDEX IF NOT EXISTS ux_owners_name            ON owners            (name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_formats_name           ON formats           (name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_format_examples_natkey ON format_examples   (format, value, is_counter);
CREATE UNIQUE INDEX IF NOT EXISTS ux_enums_name             ON enums             (name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_enum_versions_natkey   ON enum_versions     (enum, version);
CREATE UNIQUE INDEX IF NOT EXISTS ux_enum_values_natkey     ON enum_values       (enum_version, symbol);
CREATE UNIQUE INDEX IF NOT EXISTS ux_types_name             ON types             (name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_type_versions_natkey   ON type_versions     (type, version);
CREATE UNIQUE INDEX IF NOT EXISTS ux_type_attributes_natkey ON type_attributes   (type_version, attribute_name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_type_examples_natkey   ON type_examples     (type_version, idx);
CREATE UNIQUE INDEX IF NOT EXISTS ux_type_axioms_natkey     ON type_axioms       (type_version, axiom_name);
