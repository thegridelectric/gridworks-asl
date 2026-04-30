# Rulebook to PostgreSQL Script Generation Report

**Schema:** `public`
**Database:** `demo`
**Timestamp:** 2026-04-30 14:20:20 UTC

## Parsing Rulebook

Found **19** tables in rulebook

  - **Owners** (9 fields, 6 records)
  - **Formats** (11 fields, 11 records)
  - **FormatExamples** (6 fields, 82 records)
  - **Enums** (5 fields, 32 records)
  - **EnumVersions** (10 fields, 38 records)
  - **EnumValues** (5 fields, 331 records)
  - **Types** (8 fields, 46 records)
  - **TypeVersions** (10 fields, 68 records)
  - **TypeAttributes** (13 fields, 570 records)
  - **TypeExamples** (4 fields, 35 records)
  - **TypeAxioms** (6 fields, 109 records)
  - **TypeHelpers** (6 fields, 4 records)
  - **TypeHelperAttributes** (13 fields, 12 records)
  - **Projections** (5 fields, 2 records)
  - **ProjectionMappings** (5 fields, 33 records)
  - **TypeUpgrades** (5 fields, 20 records)
  - **TypeUpgradeOps** (12 fields, 25 records)
  - **EnumUpgrades** (5 fields, 0 records)
  - **EnumUpgradeMappings** (5 fields, 0 records)

Generated **19** table definitions with **99** raw fields
Generated **0** calculation functions
Generated **19** views
Enabled RLS on **19** tables
Generated insert statements for **1424** records
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

