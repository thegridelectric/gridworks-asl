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

CREATE OR REPLACE FUNCTION calc_enum_versions_word_is_retired(p_enum_versions_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enums_is_retired(enums_id)::boolean) FROM enums
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

CREATE OR REPLACE FUNCTION calc_type_versions_word_is_retired(p_type_versions_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_types_is_retired(types_id)::boolean) FROM types
   WHERE name = (SELECT type FROM type_versions WHERE type_versions_id = p_type_versions_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_format_is_retired(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_formats_is_retired(formats_id)::boolean) FROM formats
   WHERE name = (SELECT format_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_enum_is_active(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_active(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_enum_is_draft(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_enum_word_is_retired(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_word_is_retired(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_subtype_is_active(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_active(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT sub_type_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_subtype_is_draft(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_draft(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT sub_type_version_ref FROM type_attributes WHERE type_attributes_id = p_type_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_attributes_ref_subtype_word_is_retired(p_type_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_word_is_retired(type_versions_id)::boolean) FROM type_versions
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

CREATE OR REPLACE FUNCTION calc_type_axioms_word_is_retired(p_type_axioms_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_word_is_retired(type_versions_id)::boolean) FROM type_versions
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

CREATE OR REPLACE FUNCTION calc_type_helpers_is_origin_active(p_type_helpers_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_active(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helpers_is_origin_deprecated(p_type_helpers_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_deprecated(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helpers_origin_word_is_retired(p_type_helpers_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_word_is_retired(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT origin_type_version FROM type_helpers WHERE type_helpers_id = p_type_helpers_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_format_is_retired(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_formats_is_retired(formats_id)::boolean) FROM formats
   WHERE name = (SELECT format_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_enum_is_draft(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_is_draft(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_enum_word_is_retired(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_enum_versions_word_is_retired(enum_versions_id)::boolean) FROM enum_versions
   WHERE calc_enum_versions_name(enum_versions_id) = (SELECT enum_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_subtype_is_draft(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_is_draft(type_versions_id)::boolean) FROM type_versions
   WHERE calc_type_versions_name(type_versions_id) = (SELECT sub_type_version_ref FROM type_helper_attributes WHERE type_helper_attributes_id = p_type_helper_attributes_id)
   LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_helper_attributes_ref_subtype_word_is_retired(p_type_helper_attributes_id TEXT)
RETURNS BOOLEAN AS $$
  SELECT (calc_type_versions_word_is_retired(type_versions_id)::boolean) FROM type_versions
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

CREATE OR REPLACE FUNCTION calc_owners_active_type_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE calc_type_versions_owner_name(t.type_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_type_versions_is_active(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_deprecated_type_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE calc_type_versions_owner_name(t.type_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_type_versions_is_deprecated(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_draft_enum_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE calc_enum_versions_owner_name(t.enum_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_enum_versions_is_draft(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_active_enum_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE calc_enum_versions_owner_name(t.enum_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_enum_versions_is_active(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_deprecated_enum_version_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE calc_enum_versions_owner_name(t.enum_versions_id) = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_enum_versions_is_deprecated(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_retired_type_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM types t
   WHERE t.owner = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_types_is_retired(t.types_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_retired_enum_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enums t
   WHERE t.owner = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_enums_is_retired(t.enums_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_owners_retired_format_count(p_owners_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM formats t
   WHERE t.owner = (SELECT name FROM owners WHERE owners_id = p_owners_id) AND calc_formats_is_retired(t.formats_id) = TRUE;
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

CREATE OR REPLACE FUNCTION calc_enums_active_version_count(p_enums_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE t.enum = (SELECT name FROM enums WHERE enums_id = p_enums_id) AND calc_enum_versions_is_active(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_enums_deprecated_version_count(p_enums_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM enum_versions t
   WHERE t.enum = (SELECT name FROM enums WHERE enums_id = p_enums_id) AND calc_enum_versions_is_deprecated(t.enum_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_types_draft_version_count(p_types_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE t.type = (SELECT name FROM types WHERE types_id = p_types_id) AND calc_type_versions_is_draft(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_types_active_version_count(p_types_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE t.type = (SELECT name FROM types WHERE types_id = p_types_id) AND calc_type_versions_is_active(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_types_deprecated_version_count(p_types_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_versions t
   WHERE t.type = (SELECT name FROM types WHERE types_id = p_types_id) AND calc_type_versions_is_deprecated(t.type_versions_id) = TRUE;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_type_versions_stale_reference_count(p_type_versions_id TEXT)
RETURNS INTEGER AS $$
  SELECT (COUNT(*))::integer
    FROM type_attributes t
   WHERE t.type_version = calc_type_versions_name(p_type_versions_id) AND calc_type_attributes_ref_is_stale(t.type_attributes_id) = TRUE;
$$ LANGUAGE sql STABLE;

-- END aggregation overrides --
