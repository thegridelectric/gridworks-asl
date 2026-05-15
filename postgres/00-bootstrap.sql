-- ============================================================================
-- 00-BOOTSTRAP - Run first by init-db.sh (overwrite Never)
-- ============================================================================
-- Drops views and functions before the generated files recreate them.
-- Tables and their data are NEVER dropped from here — schema evolution is
-- additive (01-drop-and-create-tables.sql uses ALTER TABLE ADD COLUMN
-- IF NOT EXISTS). Views and functions are 100% derivable from the rulebook,
-- so blowing them away on every build is safe and avoids the
-- CREATE-OR-REPLACE column/signature-mismatch errors that occur when a
-- field is added, removed, or reordered.
-- ============================================================================

DO $$
DECLARE r RECORD; v_count INTEGER := 0;
BEGIN
    RAISE NOTICE 'Dropping views...';
    FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = 'public') LOOP
        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
        v_count := v_count + 1;
    END LOOP;
    RAISE NOTICE 'Dropped % views', v_count; v_count := 0;

    RAISE NOTICE 'Dropping functions...';
    FOR r IN (SELECT DISTINCT p.proname AS function_name, pg_get_function_identity_arguments(p.oid) AS function_args
                FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
               WHERE n.nspname = 'public' AND p.prokind = 'f') LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.function_name) || '(' || r.function_args || ') CASCADE';
        v_count := v_count + 1;
    END LOOP;
    RAISE NOTICE 'Dropped % functions', v_count;

    -- NOTE: tables are intentionally never dropped here. The rulebook is
    -- the SSoT for table shape, and 01-drop-and-create-tables.sql evolves
    -- them additively. Data lives in those tables (and in 05-insert-data.sql
    -- which seeds from the rulebook); blowing them away would lose any
    -- non-rulebook writes that have happened against the DB.
END $$;


