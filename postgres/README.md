# Rulebook to PostgreSQL Script Generation Report

**Schema:** `public`
**Database:** `demo`
**Timestamp:** 2026-04-30 05:32:21 UTC

## Parsing Rulebook

Found **20** tables in rulebook

  - **Owners** (9 fields, 1 records)
  - **Formats** (11 fields, 0 records)
  - **FormatExamples** (6 fields, 0 records)
  - **Enums** (4 fields, 0 records)
  - **EnumVersions** (9 fields, 0 records)
  - **EnumValues** (5 fields, 0 records)
  - **Types** (8 fields, 0 records)
  - **TypeVersions** (10 fields, 0 records)
  - **TypeAttributes** (13 fields, 0 records)
  - **TypeExamples** (4 fields, 0 records)
  - **TypeAxioms** (5 fields, 0 records)
  - **TypeHelpers** (6 fields, 0 records)
  - **TypeHelperAttributes** (13 fields, 0 records)
  - **Projections** (5 fields, 0 records)
  - **ProjectionMappings** (5 fields, 0 records)
  - **TypeUpgrades** (5 fields, 0 records)
  - **TypeUpgradeOps** (12 fields, 0 records)
  - **EnumUpgrades** (5 fields, 0 records)
  - **EnumUpgradeMappings** (5 fields, 0 records)
  - **ERBVersionsTest** (6 fields, 2 records)

Generated **20** table definitions with **102** raw fields
Generated **0** calculation functions
Generated **20** views
Enabled RLS on **20** tables
Generated insert statements for **3** records
## Script Generation Complete

Generated files:
- `00-bootstrap.sql` - Bootstrap (overwrite Never); includes commented-out drop-all script
- `01-drop-and-create-tables.sql` - Drop and recreate tables with raw fields
- `01b-customize-schema.sql` - User customizations for schema
- `02-create-functions.sql` - Create calculation functions
- `02b-customize-functions.sql` - User customizations for functions
- `03-create-views.sql` - Create views with calculated fields
- `03b-customize-views.sql` - User customizations for views
- `04-create-policies.sql` - Create RLS policies
- `04b-customize-policies.sql` - User customizations for RLS policies
- `05-insert-data.sql` - Insert data from rulebook
- `05b-customize-data.sql` - User customizations for seed data
- `init-db.sh` - Database initialization script

