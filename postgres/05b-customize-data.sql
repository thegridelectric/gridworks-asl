-- ============================================================================
-- 05b-customize-data.sql — sema customizations applied AFTER 05-insert-data
-- ============================================================================
-- sema has no Airtable. This file's sole job is to chain in the
-- auto-generated 05c-install-vocabulary.sql, which contains the YAML SSoT
-- vocabulary upserts (regenerate via src/sema/tools/sync_vocabulary_to_db.py).
--
-- Idempotent: 05c uses INSERT ... ON CONFLICT DO UPDATE for every row, so
-- re-running init-db.sh always converges the DB to the YAML's current state.
-- ============================================================================

\ir 05c-install-vocabulary.sql
