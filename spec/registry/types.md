# Registry — Type Entries

This sub-spec covers `registry.yaml` entries for **types**, including
versioning semantics, strategy evolution, new-version publication,
immutability, and the dependency model. For writing the type schema files
themselves, see [../authoring/types.md](../authoring/types.md). For
cross-cutting registry shape, see [structure.md](structure.md).

Read [../primary.md](../primary.md) for core principles.

## Type Entry

Each type entry in the registry SHALL declare a `versioning_strategy` and
SHALL conform to one of the structures defined below.

```
<type-name>:
  owner: <owner-id>
  versioning_strategy: "none" | "string" | "literal"
  description: "<concise semantic description>"
```

## Versioning Semantics

### Versioned vs Versionless Types

- Types with `versioning_strategy: "none"` are **versionless**.
- Types with `versioning_strategy: "string"` or `"literal"` are
  **versioned**.

### Version Format

Versions SHALL be **numeric strings of exactly three digits**.

Examples: `"000"`, `"001"`, `"013"`.

### Ordering and Uniqueness

- Each version SHALL be unique within the type.
- Each version entry SHALL include a `created` timestamp (see
  *New Versions* below).
- The `created` timestamp SHALL be unique across all versions of the type.
- For any two versions `v_old` and `v_new`: if `v_new` is numerically
  greater than `v_old`, then `created(v_new)` SHALL be strictly later
  than `created(v_old)`.
- For any version entry `v`, `created(v)` SHALL be no earlier than the
  `created` timestamp of every vocabulary word named in that version's
  `direct_dependencies`.

### Preferred Baseline Version

`"000"` SHOULD be used as the initial version of a versioned type, but
this is not required.

## Versioned Type Structure

A versioned type entry SHALL include the following fields:

```
<type-name>:
  latest_version: "<version>"
  owner: <owner-id>
  versioning_strategy: "literal" | "string"
  description: "<concise semantic description>"

  versions:
    "<version>":
      status: "published" | "draft"   # optional; default published
      schema_url: "https://schemas.electricity.works/types/<type-name>/<version>"
      created: "<RFC 3339 timestamp>"
      summary: "<concise description of change>"
      direct_dependencies:
        structural:
          - "<dependency>"
        axiom:
          - "<dependency>"
    [..]  # earlier versions
```

### Field Requirements

- `latest_version`
  - SHALL equal the highest published version listed under `versions`
  - SHALL NOT identify a draft version

- `owner`
  - SHALL reference a valid owner identifier defined in `owners.yaml`

- `versions`
  - SHALL contain an entry for each published version of the type
  - MAY contain draft version entries
  - SHALL be keyed by version string
  - SHALL be listed in decreasing order by version
  - The keys of `versions` SHALL match the `<version>` values used within
    each entry

### Version Entry Requirements

Each entry under `versions` SHALL include:

- `schema_url`
  - SHALL uniquely identify the schema for that version

- `status`
  - MAY appear
  - SHALL be `"published"` or `"draft"` if present
  - SHALL be interpreted as `"published"` if omitted

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC (e.g.,
    `YYYY-MM-DDTHH:mm:ssZ`)

- `summary`
  - SHALL describe the change introduced in that version

- `direct_dependencies`
  - SHALL conform to the rules defined in *Dependency Model* below

## Versionless Type Structure

A versionless type entry SHALL include the following fields:

```yaml
<type-name>:
  owner: <owner-id>
  versioning_strategy: "none"
  description: "<concise semantic description>"

  schema_url: "https://schemas.electricity.works/types/<type-name>"
  created: "<RFC 3339 timestamp>"

  direct_dependencies:
    structural:
      - "<dependency>"
```

### Field Requirements

- `owner`
  - SHALL reference a valid owner identifier defined in `owners.yaml`

- Versionless types SHALL NOT include a `versions` field

- `schema_url`
  - SHALL NOT include a version segment
  - SHALL uniquely identify the schema for the type

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC

- `direct_dependencies`
  - SHALL conform to the rules defined in *Dependency Model* below

## Strategy Semantics

The `literal` and `string` strategies differ only in schema validation
behavior.

- `literal` enforces exact version matching in the schema
- `string` allows a schema to validate multiple versions

Both strategies:
- SHALL require all versions to be explicitly listed in the registry
- SHALL require versions to be strictly ordered
- SHALL require runtime upgrade chains to resolve messages to the latest
  version

## Versioning Strategy Evolution

The `versioning_strategy` evolution through time for a type SHALL follow a
monotonic strictness model:

```
none -> string -> literal
```

A type MAY transition only to a strictly more constrained strategy.

Permitted transitions:
- `none` → `string`
- `none` → `literal`
- `string` → `literal`

Prohibited transitions:
- `literal` → `string`
- `literal` → `none`
- `string` → `none`

Once a type adopts a stricter strategy, it SHALL NOT revert to a less
strict strategy.

### Transition from Versionless to Versioned

If a type with `versioning_strategy: "none"` adopts versioning:

- The registry SHALL be updated to reflect the new strategy
- A versioned lineage SHALL be established under `versions`
- The initial version SHOULD be `"000"`

A schema SHALL be published at:

```
https://schemas.electricity.works/types/<type-name>/000
```

The following SHALL hold:

- The original versionless schema URL SHALL remain accessible
- The original schema SHALL NOT be retroactively modified or assigned a
  version number

Versioning begins at the point versioned schemas are introduced.

## New Versions (Creation and Publication)

A new version of a versioned type SHALL be published when required and
SHALL be recorded in the registry as defined below.

### When a New Version Is Required

A new version SHALL be published if any of the following occur:

- A required property is added or removed
- A property type or constraint changes
- A referenced enum or type version changes
- An axiom is added, removed, or modified
- Validation constraints are strengthened or relaxed
- Semantic meaning changes

A new version SHOULD be published if:

- Property descriptions are clarified in a way that could affect
  interpretation
- Architectural meaning changes in a non-trivial way

A new version MAY be published for:

- Documentation or example improvements

### Publishing a New Version

When publishing a new version, the registry SHALL be updated as follows:

- A new entry SHALL be added under `versions` for the new version:

  ```yaml
  versions:
    "<new_version>":
      schema_url: "https://schemas.electricity.works/types/<type-name>/<new_version>"
      created: "<RFC 3339 timestamp>"
      summary: "<concise description of change>"
      direct_dependencies:
        structural:
          - ...
        axiom:
          - ...
  ```

- `latest_version` SHALL be updated to the new version:

  ```yaml
  latest_version: "<new_version>"
  ```

### Preservation of Prior Versions

- All previously published versions SHALL remain listed in the registry
- Previously published schema URLs SHALL remain accessible

Additional constraints on modification of prior versions are defined in
*Immutability* below.

## Immutability

Sema registry entries are immutable except as explicitly permitted below.
Types with `status: "draft"` are exempt from these immutability
requirements.

### General Rules (All Types)

- The schema referenced by `schema_url` SHALL NOT be modified in a way
  that changes validation behavior
- Registry entries SHALL NOT be modified in a way that changes semantics

### Versioned Types (Additional Constraints)

- Version identifiers (the keys under `versions`) SHALL NOT be changed or
  removed
- New version identifiers MAY be added in accordance with the rules
  defined in *New Versions (Creation and Publication)*

### Permitted Changes (All Types)

The following changes are permitted, provided they do not alter semantics:

- Correction of typographical errors
- Clarification of descriptive text
- Correction of `created` timestamps, provided that:
  - Timestamp uniqueness is preserved
  - Timestamp ordering remains consistent with version ordering as
    defined in *Versioning Semantics*

### Ownership Transfer

The `owner` field MAY be updated to transfer ownership of a type,
provided that:

- The transfer is explicitly authorized by the current owner
- The new owner identifier is valid and defined in `owners.yaml`
- The transfer does not alter the semantics of the type or any of its
  versions

Ownership transfer SHALL NOT affect:
- Version history
- Schema behavior
- Dependency declarations

Ownership transfer history is not tracked in the registry.

### Versionless Types

Versionless types SHALL NOT be modified in a way that changes semantics.
If a semantic change is required, the rules defined in *Versioning
Strategy Evolution* SHALL be followed.

## Dependency Model

Versioned types SHALL declare direct dependencies. These identify the
Sema vocabulary required to:

- validate the schema structurally
- implement any axioms attached to that specific type version

Dependencies are expressed in `registry.yaml` as:

```yaml
direct_dependencies:
  structural:
    - "<word-name>:<version>"   # enums or versioned types
    - "<word-name>"             # formats or versionless types
  axiom:
    - "<word-name>:<version>"
    - "<word-name>"
```

### Structural Dependencies

- SHALL include every vocabulary word explicitly referenced in the schema
  via `$ref`
- SHALL use the canonical identifier format:
  - `name:###` for enums and versioned types (3-digit numeric version)
  - `name` for formats and versionless types
- SHALL NOT include transitive dependencies

### Axiom Dependencies

- SHALL include every Sema vocabulary word *not* in the structural
  dependencies required to implement one or more axioms for that type
  version
- SHALL be included even if the vocabulary is not referenced via `$ref`
- SHALL use the same canonical identifier rules as `structural`
- SHALL NOT include transitive dependencies

### Structure and Ordering

- `structural` and `axiom` (if present) SHALL:
  - be sorted lexicographically by full identifier string
  - contain no duplicates
  - be declared as block lists (one entry per line)
- Dependency references SHALL NOT include URL prefixes or file paths
- If no dependencies exist, the dependency block SHALL be:

  ```
  direct_dependencies:
    structural: []
  ```

- If structural dependencies exist but no axiom-level dependencies exist,
  `axiom` SHOULD be omitted.
- If structural dependencies do not exist but axiom-level dependencies do
  exist, `structural` SHALL be declared as `[]`.

### Version Rules

- Versioned words MUST be referenced as `name:###` where `###` is a
  3-digit numeric string.
- Versionless words MUST NOT include a version suffix.
- Mixing formats (e.g., including a colon for versionless words or
  omitting a version for versioned words) is invalid.

### Axiom Implementability

- Dependency declaration SHALL be sufficient to implement validation for
  the full contract of the type version, including its axioms.
- If an axiom normatively names a specific Sema vocabulary word or
  version, that word SHALL appear in `axiom` unless it already appears in
  `structural`.
- A type version SHALL NOT rely on undeclared external Sema vocabulary to
  make its axioms mechanically implementable.
