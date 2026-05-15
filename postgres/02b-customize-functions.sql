-- ============================================================================
-- AUTO-GENERATED OVERRIDE — fixes lookup functions whose generated bodies
-- match by `<target>_id` (UUID PK) instead of `<target>.<MatchField>`.
-- Regenerate with scripts/fix_lookup_functions.py after every effortless build.
-- ============================================================================

CREATE OR REPLACE FUNCTION calc_formats_owner_name(p_formats_id TEXT)
RETURNS TEXT AS $$
  SELECT (name::text) FROM owners
   WHERE name = (SELECT owner FROM formats WHERE formats_id = p_formats_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_versions_owner_name(p_enum_versions_id TEXT)
RETURNS TEXT AS $$
  SELECT (owner::text) FROM enums
   WHERE name = (SELECT enum FROM enum_versions WHERE enum_versions_id = p_enum_versions_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_versions_word_description(p_enum_versions_id TEXT)
RETURNS TEXT AS $$
  SELECT (description::text) FROM enums
   WHERE name = (SELECT enum FROM enum_versions WHERE enum_versions_id = p_enum_versions_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_versions_owner_name(p_type_versions_id TEXT)
RETURNS TEXT AS $$
  SELECT (owner::text) FROM types
   WHERE name = (SELECT type FROM type_versions WHERE type_versions_id = p_type_versions_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_versions_word_title(p_type_versions_id TEXT)
RETURNS TEXT AS $$
  SELECT (title::text) FROM types
   WHERE name = (SELECT type FROM type_versions WHERE type_versions_id = p_type_versions_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_enum_is_draft(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_subtype_is_draft(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_draft(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT sub_type_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_examples_owner_name(p_type_examples_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_type_versions_owner_name(type_versions_id)::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT type_version FROM type_examples WHERE type_examples_id = p_type_examples_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_axioms_owner_name(p_type_axioms_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_type_versions_owner_name(type_versions_id)::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT type_version FROM type_axioms WHERE type_axioms_id = p_type_axioms_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helpers_origin_owner_name(p_type_helpers_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_type_versions_owner_name(type_versions_id)::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helpers_origin_type_name(p_type_helpers_id TEXT)
RETURNS TEXT AS $$
  SELECT (type::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helpers_is_origin_draft(p_type_helpers_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_draft(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_enum_is_draft(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_subtype_is_draft(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_draft(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT sub_type_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_from_owner_name(p_projections_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_enum_versions_owner_name(enum_versions_id)::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_to_owner_name(p_projections_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_enum_versions_owner_name(enum_versions_id)::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT to_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_from_enum_name(p_projections_id TEXT)
RETURNS TEXT AS $$
  SELECT (enum::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_to_enum_name(p_projections_id TEXT)
RETURNS TEXT AS $$
  SELECT (enum::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT to_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_from_is_draft(p_projections_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_projections_to_is_draft(p_projections_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT to_enum_version FROM projections WHERE projections_id = p_projections_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_upgrades_from_word(p_type_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (type::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT from_type_version FROM type_upgrades WHERE type_upgrades_id = p_type_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_upgrades_to_word(p_type_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (type::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT to_type_version FROM type_upgrades WHERE type_upgrades_id = p_type_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_upgrades_from_version(p_type_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (version::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT from_type_version FROM type_upgrades WHERE type_upgrades_id = p_type_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_upgrades_to_version(p_type_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (version::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT to_type_version FROM type_upgrades WHERE type_upgrades_id = p_type_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_upgrades_owner_name(p_type_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_type_versions_owner_name(type_versions_id)::text) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT from_type_version FROM type_upgrades WHERE type_upgrades_id = p_type_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_upgrades_from_word(p_enum_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (enum::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM enum_upgrades WHERE enum_upgrades_id = p_enum_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_upgrades_to_word(p_enum_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (enum::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT to_enum_version FROM enum_upgrades WHERE enum_upgrades_id = p_enum_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_upgrades_from_version(p_enum_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (version::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM enum_upgrades WHERE enum_upgrades_id = p_enum_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_upgrades_to_version(p_enum_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (version::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT to_enum_version FROM enum_upgrades WHERE enum_upgrades_id = p_enum_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enum_upgrades_owner_name(p_enum_upgrades_id TEXT)
RETURNS TEXT AS $$
  SELECT (calc_enum_versions_owner_name(enum_versions_id)::text) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT from_enum_version FROM enum_upgrades WHERE enum_upgrades_id = p_enum_upgrades_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

-- BEGIN aggregation overrides --
-- 18 aggregation overrides for fields whose criteria_range
-- references calc/lookup/aggregation columns. The transpiler silently
-- drops those criteria; we restore them here. Auto-generated by
-- scripts/fix_aggregations.py.

CREATE OR REPLACE FUNCTION calc_owners_draft_type_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE calc_type_versions_owner_name(t.type_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_type_versions_is_draft(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_draft_enum_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE calc_enum_versions_owner_name(t.enum_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_enum_versions_is_draft(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_latest_type_version_at(p_owners_id TEXT)
RETURNS TIMESTAMPTZ AS $$
  SELECT (MAX(t.created))::timestamptz
    FROM type_versions t
   WHERE calc_type_versions_owner_name(t.type_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id);
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_latest_enum_version_at(p_owners_id TEXT)
RETURNS TIMESTAMPTZ AS $$
  SELECT (MAX(t.created))::timestamptz
    FROM enum_versions t
   WHERE calc_enum_versions_owner_name(t.enum_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id);
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enums_draft_version_count(p_enums_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE t.enum = (SELECT name FROM enums WHERE enums_id = p_enums_id) AND calc_enum_versions_is_draft(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_types_draft_version_count(p_types_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE t.type = (SELECT name FROM types WHERE types_id = p_types_id) AND calc_type_versions_is_draft(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_enum_version_exists(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT CASE
    WHEN (SELECT NULLIF(enum_version_ref, '') FROM type_attributes WHERE type_attributes_id = p_type_attributes_id) IS NULL THEN TRUE
    ELSE EXISTS(
      SELECT 1 FROM enum_versions ev
       WHERE ev.enum    = split_part((SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id), '/', 1)
         AND ev.version = split_part((SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id), '/', 2)
    )
  END;
$$ LANGUAGE sql STABLE;

-- type_attributes.ref_sub_type_version_exists: split "<type>/<version>" then EXISTS
CREATE OR REPLACE FUNCTION calc_type_attributes_ref_sub_type_version_exists(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT CASE
    WHEN (SELECT NULLIF(sub_type_version_ref, '') FROM type_attributes WHERE type_attributes_id = p_type_attributes_id) IS NULL THEN TRUE
    ELSE EXISTS(
      SELECT 1 FROM type_versions tv
       WHERE tv.type    = split_part((SELECT sub_type_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id), '/', 1)
         AND tv.version = split_part((SELECT sub_type_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id), '/', 2)
    )
  END;
$$ LANGUAGE sql STABLE;

-- type_helper_attributes mirrors of the above (HelperAttributes have the same ref columns)
CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_enum_version_exists(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT CASE
    WHEN (SELECT NULLIF(enum_version_ref, '') FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id) IS NULL THEN TRUE
    ELSE EXISTS(
      SELECT 1 FROM enum_versions ev
       WHERE ev.enum    = split_part((SELECT enum_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id), '/', 1)
         AND ev.version = split_part((SELECT enum_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id), '/', 2)
    )
  END;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_sub_type_version_exists(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT CASE
    WHEN (SELECT NULLIF(sub_type_version_ref, '') FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id) IS NULL THEN TRUE
    ELSE EXISTS(
      SELECT 1 FROM type_versions tv
       WHERE tv.type    = split_part((SELECT sub_type_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id), '/', 1)
         AND tv.version = split_part((SELECT sub_type_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id), '/', 2)
    )
  END;
$$ LANGUAGE sql STABLE;

-- type_versions.unresolved_ref_count: count attributes where the AND of
-- format/enum/subtype-exists is FALSE.
CREATE OR REPLACE FUNCTION calc_type_versions_unresolved_ref_count(p_type_versions_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM type_attributes ta
   WHERE ta.type_version = (SELECT type || '/' || version FROM type_versions WHERE type_versions_id = p_type_versions_id)
     AND calc_type_attributes_ref_is_resolvable(ta.type_attributes_id) = FALSE;
$$ LANGUAGE sql STABLE;

-- type_helpers.unresolved_ref_count: same against type_helper_attributes
CREATE OR REPLACE FUNCTION calc_type_helpers_unresolved_ref_count(p_type_helpers_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM type_helper_attributes tha
   WHERE tha.type_helper = (SELECT name FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
     AND calc_type_helper_attributes_ref_is_resolvable(tha.type_helper_attributes_id) = FALSE;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- Active->Published rename overrides. The 02b active-named overrides above are
-- orphans now; these re-implement the same logic under the renamed function
-- names that match the rulebook's Published* aggregations.
-- ============================================================================

CREATE OR REPLACE FUNCTION calc_types_published_version_count(p_types_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM type_versions tv
   WHERE tv.type = (SELECT name FROM types WHERE types_id = p_types_id)
     AND calc_type_versions_is_published(tv.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enums_published_version_count(p_enums_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM enum_versions ev
   WHERE ev.enum = (SELECT name FROM enums WHERE enums_id = p_enums_id)
     AND calc_enum_versions_is_published(ev.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_published_type_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM type_versions tv
   WHERE tv.type IN (SELECT t.name FROM types t WHERE t.owner = (SELECT name FROM owners WHERE owners_id = p_owners_id))
     AND calc_type_versions_is_published(tv.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_published_enum_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::integer
    FROM enum_versions ev
   WHERE ev.enum IN (SELECT e.name FROM enums e WHERE e.owner = (SELECT name FROM owners WHERE owners_id = p_owners_id))
     AND calc_enum_versions_is_published(ev.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;
