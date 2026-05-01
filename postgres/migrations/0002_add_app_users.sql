-- ============================================================================
-- 0002_add_app_users.sql
-- ============================================================================
-- First post-bootstrap rulebook change: add the AppUsers table that gates
-- magic-links login. Without this row in the DB, the AppUsers allowlist
-- check in app/api/auth.py rejects every JWT (since vw_app_users is empty
-- or absent) and nobody can log in.
--
-- Mirrors the DDL emitted by rulebook-to-postgres for AppUsers (PK
-- auto-synthesized as app_users_id since the rulebook has no Id field;
-- the email lives in `name` as a regular column, not the PK).
--
-- Idempotent — uses IF NOT EXISTS / OR REPLACE / ON CONFLICT, so rerunning
-- against a base that already has it is a no-op.
-- ============================================================================

-- 1. Table -------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS app_users (
    app_users_id  TEXT        PRIMARY KEY,
    name          TEXT,
    display_name  TEXT,
    role          TEXT,
    notes         TEXT,
    created       TIMESTAMPTZ
);

-- 2. Calculated-field functions ---------------------------------------------

CREATE OR REPLACE FUNCTION calc_app_users_is_admin(p_app_users_id TEXT)
RETURNS BOOLEAN AS $$
    SELECT (
        CASE WHEN (SELECT NULLIF(role, '') FROM app_users WHERE app_users_id = p_app_users_id) = 'admin'
             THEN TRUE ELSE FALSE END
    )::boolean;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_app_users_is_member(p_app_users_id TEXT)
RETURNS BOOLEAN AS $$
    SELECT (
        CASE WHEN (SELECT NULLIF(role, '') FROM app_users WHERE app_users_id = p_app_users_id) = 'member'
             THEN TRUE ELSE FALSE END
    )::boolean;
$$ LANGUAGE sql STABLE;

-- 3. View (the read surface — auth.py gates on vw_app_users) ----------------

CREATE OR REPLACE VIEW vw_app_users WITH (security_invoker = ON) AS
SELECT
    t.app_users_id,
    t.name,
    t.display_name,
    t.role,
    t.notes,
    t.created,
    calc_app_users_is_admin(t.app_users_id)  AS is_admin,
    calc_app_users_is_member(t.app_users_id) AS is_member
FROM app_users t;

-- 4. RLS (matches the posture of the other 19 tables: enabled, no policies;
--        admin owns the table and bypasses RLS as the app's DB role) -------

ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;

-- 5. Bootstrap admin ---------------------------------------------------------
-- Mirrors the seed row in postgres/05-insert-data.sql. Without at least one
-- row, the gate locks prod out entirely.

INSERT INTO app_users (app_users_id, name, display_name, role, notes, created)
VALUES (
    '3856874c-b33c-c3a2-e615-f12a305393bd',
    'ej@ssot.me',
    'EJ',
    'admin',
    'Bootstrap admin (seeded with the initial AppUsers landing).',
    '2026-04-30T23:30:00Z'::timestamptz
)
ON CONFLICT (app_users_id) DO NOTHING;
