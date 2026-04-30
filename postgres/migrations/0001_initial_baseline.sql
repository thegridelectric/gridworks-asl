-- ============================================================================
-- 0001_initial_baseline.sql
-- ============================================================================
-- This migration carries no DDL. It exists so that the day-of-bootstrap
-- INSERT into public.schema_migrations happens through the same channel
-- every subsequent migration uses, keeping the audit trail consistent.
--
-- On the day prod is bootstrapped:
--   1. ./postgres/init-db.sh "$BASE_ADMIN_URL"   ← creates the schema
--   2. psql … -f 01b-customize-schema.sql is included in step 1
--   3. (insert auth.trusted_tenants row)
--   4. ./postgres/migrations/migrate-prod.sh "$BASE_ADMIN_URL"
--      ← applies this file, recording version 0001 in schema_migrations,
--        which is what tells future runs "the baseline is in place."
--
-- After this, every rulebook change ships as 0002, 0003, … in this dir.
-- ============================================================================

-- No-op. The migrate-prod.sh runner records the version for us.
SELECT 1 AS baseline_recorded;
