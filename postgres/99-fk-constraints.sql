-- ============================================================================
-- 99-fk-constraints.sql — FK CONSTRAINTS (off by default)
-- ============================================================================
-- Demos must never fail on FK violations, so init-db.sh SKIPS this file
-- unless EFFORTLESS_ENFORCE_FKS=true is set in the environment.
--
--   EFFORTLESS_ENFORCE_FKS=true bash init-db.sh    # apply constraints
--   bash init-db.sh                                # leave them documented but unenforced
--
-- The rulebook always documents the FK relationships, and 01-drop-and-create-tables.sql
-- always installs the supporting indexes inline. This file just declares the actual
-- enforcement. Idempotent: every constraint is dropped if present, then added.
-- ============================================================================

-- Formats
ALTER TABLE formats DROP CONSTRAINT IF EXISTS fk_formats_owner;
ALTER TABLE formats ADD CONSTRAINT fk_formats_owner
  FOREIGN KEY (owner) REFERENCES owners (owners_id);
ALTER TABLE formats DROP CONSTRAINT IF EXISTS fk_formats_replaced_by;
ALTER TABLE formats ADD CONSTRAINT fk_formats_replaced_by
  FOREIGN KEY (replaced_by) REFERENCES formats (formats_id);

-- FormatExamples
ALTER TABLE format_examples DROP CONSTRAINT IF EXISTS fk_format_examples_format;
ALTER TABLE format_examples ADD CONSTRAINT fk_format_examples_format
  FOREIGN KEY (format) REFERENCES formats (formats_id);

-- Enums
ALTER TABLE enums DROP CONSTRAINT IF EXISTS fk_enums_owner;
ALTER TABLE enums ADD CONSTRAINT fk_enums_owner
  FOREIGN KEY (owner) REFERENCES owners (owners_id);
ALTER TABLE enums DROP CONSTRAINT IF EXISTS fk_enums_replaced_by;
ALTER TABLE enums ADD CONSTRAINT fk_enums_replaced_by
  FOREIGN KEY (replaced_by) REFERENCES enums (enums_id);

-- EnumVersions
ALTER TABLE enum_versions DROP CONSTRAINT IF EXISTS fk_enum_versions_enum;
ALTER TABLE enum_versions ADD CONSTRAINT fk_enum_versions_enum
  FOREIGN KEY (enum) REFERENCES enums (enums_id);

-- EnumValues
ALTER TABLE enum_values DROP CONSTRAINT IF EXISTS fk_enum_values_enum_version;
ALTER TABLE enum_values ADD CONSTRAINT fk_enum_values_enum_version
  FOREIGN KEY (enum_version) REFERENCES enum_versions (enum_versions_id);

-- Types
ALTER TABLE types DROP CONSTRAINT IF EXISTS fk_types_owner;
ALTER TABLE types ADD CONSTRAINT fk_types_owner
  FOREIGN KEY (owner) REFERENCES owners (owners_id);
ALTER TABLE types DROP CONSTRAINT IF EXISTS fk_types_replaced_by;
ALTER TABLE types ADD CONSTRAINT fk_types_replaced_by
  FOREIGN KEY (replaced_by) REFERENCES types (types_id);

-- TypeVersions
ALTER TABLE type_versions DROP CONSTRAINT IF EXISTS fk_type_versions_type;
ALTER TABLE type_versions ADD CONSTRAINT fk_type_versions_type
  FOREIGN KEY (type) REFERENCES types (types_id);

-- TypeAttributes
ALTER TABLE type_attributes DROP CONSTRAINT IF EXISTS fk_type_attributes_type_version;
ALTER TABLE type_attributes ADD CONSTRAINT fk_type_attributes_type_version
  FOREIGN KEY (type_version) REFERENCES type_versions (type_versions_id);
ALTER TABLE type_attributes DROP CONSTRAINT IF EXISTS fk_type_attributes_format_ref;
ALTER TABLE type_attributes ADD CONSTRAINT fk_type_attributes_format_ref
  FOREIGN KEY (format_ref) REFERENCES formats (formats_id);
ALTER TABLE type_attributes DROP CONSTRAINT IF EXISTS fk_type_attributes_enum_version_ref;
ALTER TABLE type_attributes ADD CONSTRAINT fk_type_attributes_enum_version_ref
  FOREIGN KEY (enum_version_ref) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE type_attributes DROP CONSTRAINT IF EXISTS fk_type_attributes_sub_type_version_ref;
ALTER TABLE type_attributes ADD CONSTRAINT fk_type_attributes_sub_type_version_ref
  FOREIGN KEY (sub_type_version_ref) REFERENCES type_versions (type_versions_id);
ALTER TABLE type_attributes DROP CONSTRAINT IF EXISTS fk_type_attributes_helper_ref;
ALTER TABLE type_attributes ADD CONSTRAINT fk_type_attributes_helper_ref
  FOREIGN KEY (helper_ref) REFERENCES type_helpers (type_helpers_id);

-- TypeExamples
ALTER TABLE type_examples DROP CONSTRAINT IF EXISTS fk_type_examples_type_version;
ALTER TABLE type_examples ADD CONSTRAINT fk_type_examples_type_version
  FOREIGN KEY (type_version) REFERENCES type_versions (type_versions_id);

-- TypeAxioms
ALTER TABLE type_axioms DROP CONSTRAINT IF EXISTS fk_type_axioms_type_version;
ALTER TABLE type_axioms ADD CONSTRAINT fk_type_axioms_type_version
  FOREIGN KEY (type_version) REFERENCES type_versions (type_versions_id);

-- TypeHelpers
ALTER TABLE type_helpers DROP CONSTRAINT IF EXISTS fk_type_helpers_origin_type_version;
ALTER TABLE type_helpers ADD CONSTRAINT fk_type_helpers_origin_type_version
  FOREIGN KEY (origin_type_version) REFERENCES type_versions (type_versions_id);

-- TypeHelperAttributes
ALTER TABLE type_helper_attributes DROP CONSTRAINT IF EXISTS fk_type_helper_attributes_type_helper;
ALTER TABLE type_helper_attributes ADD CONSTRAINT fk_type_helper_attributes_type_helper
  FOREIGN KEY (type_helper) REFERENCES type_helpers (type_helpers_id);
ALTER TABLE type_helper_attributes DROP CONSTRAINT IF EXISTS fk_type_helper_attributes_format_ref;
ALTER TABLE type_helper_attributes ADD CONSTRAINT fk_type_helper_attributes_format_ref
  FOREIGN KEY (format_ref) REFERENCES formats (formats_id);
ALTER TABLE type_helper_attributes DROP CONSTRAINT IF EXISTS fk_type_helper_attributes_enum_version_ref;
ALTER TABLE type_helper_attributes ADD CONSTRAINT fk_type_helper_attributes_enum_version_ref
  FOREIGN KEY (enum_version_ref) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE type_helper_attributes DROP CONSTRAINT IF EXISTS fk_type_helper_attributes_sub_type_version_ref;
ALTER TABLE type_helper_attributes ADD CONSTRAINT fk_type_helper_attributes_sub_type_version_ref
  FOREIGN KEY (sub_type_version_ref) REFERENCES type_versions (type_versions_id);
ALTER TABLE type_helper_attributes DROP CONSTRAINT IF EXISTS fk_type_helper_attributes_helper_ref;
ALTER TABLE type_helper_attributes ADD CONSTRAINT fk_type_helper_attributes_helper_ref
  FOREIGN KEY (helper_ref) REFERENCES type_helpers (type_helpers_id);

-- Projections
ALTER TABLE projections DROP CONSTRAINT IF EXISTS fk_projections_from_enum_version;
ALTER TABLE projections ADD CONSTRAINT fk_projections_from_enum_version
  FOREIGN KEY (from_enum_version) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE projections DROP CONSTRAINT IF EXISTS fk_projections_to_enum_version;
ALTER TABLE projections ADD CONSTRAINT fk_projections_to_enum_version
  FOREIGN KEY (to_enum_version) REFERENCES enum_versions (enum_versions_id);

-- ProjectionMappings
ALTER TABLE projection_mappings DROP CONSTRAINT IF EXISTS fk_projection_mappings_projection;
ALTER TABLE projection_mappings ADD CONSTRAINT fk_projection_mappings_projection
  FOREIGN KEY (projection) REFERENCES projections (projections_id);

-- TypeUpgrades
ALTER TABLE type_upgrades DROP CONSTRAINT IF EXISTS fk_type_upgrades_from_type_version;
ALTER TABLE type_upgrades ADD CONSTRAINT fk_type_upgrades_from_type_version
  FOREIGN KEY (from_type_version) REFERENCES type_versions (type_versions_id);
ALTER TABLE type_upgrades DROP CONSTRAINT IF EXISTS fk_type_upgrades_to_type_version;
ALTER TABLE type_upgrades ADD CONSTRAINT fk_type_upgrades_to_type_version
  FOREIGN KEY (to_type_version) REFERENCES type_versions (type_versions_id);

-- TypeUpgradeOps
ALTER TABLE type_upgrade_ops DROP CONSTRAINT IF EXISTS fk_type_upgrade_ops_type_upgrade;
ALTER TABLE type_upgrade_ops ADD CONSTRAINT fk_type_upgrade_ops_type_upgrade
  FOREIGN KEY (type_upgrade) REFERENCES type_upgrades (type_upgrades_id);
ALTER TABLE type_upgrade_ops DROP CONSTRAINT IF EXISTS fk_type_upgrade_ops_enum_version_ref;
ALTER TABLE type_upgrade_ops ADD CONSTRAINT fk_type_upgrade_ops_enum_version_ref
  FOREIGN KEY (enum_version_ref) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE type_upgrade_ops DROP CONSTRAINT IF EXISTS fk_type_upgrade_ops_projection_ref;
ALTER TABLE type_upgrade_ops ADD CONSTRAINT fk_type_upgrade_ops_projection_ref
  FOREIGN KEY (projection_ref) REFERENCES projections (projections_id);

-- EnumUpgrades
ALTER TABLE enum_upgrades DROP CONSTRAINT IF EXISTS fk_enum_upgrades_from_enum_version;
ALTER TABLE enum_upgrades ADD CONSTRAINT fk_enum_upgrades_from_enum_version
  FOREIGN KEY (from_enum_version) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE enum_upgrades DROP CONSTRAINT IF EXISTS fk_enum_upgrades_to_enum_version;
ALTER TABLE enum_upgrades ADD CONSTRAINT fk_enum_upgrades_to_enum_version
  FOREIGN KEY (to_enum_version) REFERENCES enum_versions (enum_versions_id);

-- EnumUpgradeMappings
ALTER TABLE enum_upgrade_mappings DROP CONSTRAINT IF EXISTS fk_enum_upgrade_mappings_enum_upgrade;
ALTER TABLE enum_upgrade_mappings ADD CONSTRAINT fk_enum_upgrade_mappings_enum_upgrade
  FOREIGN KEY (enum_upgrade) REFERENCES enum_upgrades (enum_upgrades_id);

-- SeedRequests
ALTER TABLE seed_requests DROP CONSTRAINT IF EXISTS fk_seed_requests_owner;
ALTER TABLE seed_requests ADD CONSTRAINT fk_seed_requests_owner
  FOREIGN KEY (owner) REFERENCES owners (owners_id);

-- SeedRequestEntries
ALTER TABLE seed_request_entries DROP CONSTRAINT IF EXISTS fk_seed_request_entries_seed_request;
ALTER TABLE seed_request_entries ADD CONSTRAINT fk_seed_request_entries_seed_request
  FOREIGN KEY (seed_request) REFERENCES seed_requests (seed_requests_id);

-- Snapshots
ALTER TABLE snapshots DROP CONSTRAINT IF EXISTS fk_snapshots_seed_request;
ALTER TABLE snapshots ADD CONSTRAINT fk_snapshots_seed_request
  FOREIGN KEY (seed_request) REFERENCES seed_requests (seed_requests_id);

-- LocalNames
ALTER TABLE local_names DROP CONSTRAINT IF EXISTS fk_local_names_snapshot;
ALTER TABLE local_names ADD CONSTRAINT fk_local_names_snapshot
  FOREIGN KEY (snapshot) REFERENCES snapshots (snapshots_id);

-- Templates
ALTER TABLE templates DROP CONSTRAINT IF EXISTS fk_templates_axiom_type_version;
ALTER TABLE templates ADD CONSTRAINT fk_templates_axiom_type_version
  FOREIGN KEY (axiom_type_version) REFERENCES type_versions (type_versions_id);
ALTER TABLE templates DROP CONSTRAINT IF EXISTS fk_templates_upgrade_from_type_version;
ALTER TABLE templates ADD CONSTRAINT fk_templates_upgrade_from_type_version
  FOREIGN KEY (upgrade_from_type_version) REFERENCES type_versions (type_versions_id);
ALTER TABLE templates DROP CONSTRAINT IF EXISTS fk_templates_upgrade_to_type_version;
ALTER TABLE templates ADD CONSTRAINT fk_templates_upgrade_to_type_version
  FOREIGN KEY (upgrade_to_type_version) REFERENCES type_versions (type_versions_id);
ALTER TABLE templates DROP CONSTRAINT IF EXISTS fk_templates_upgrade_from_enum_version;
ALTER TABLE templates ADD CONSTRAINT fk_templates_upgrade_from_enum_version
  FOREIGN KEY (upgrade_from_enum_version) REFERENCES enum_versions (enum_versions_id);
ALTER TABLE templates DROP CONSTRAINT IF EXISTS fk_templates_upgrade_to_enum_version;
ALTER TABLE templates ADD CONSTRAINT fk_templates_upgrade_to_enum_version
  FOREIGN KEY (upgrade_to_enum_version) REFERENCES enum_versions (enum_versions_id);

-- 43 FK constraint(s) declared (off unless EFFORTLESS_ENFORCE_FKS=true).
