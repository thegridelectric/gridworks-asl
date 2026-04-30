# Sema Specification

Version 1.0


A Shared Vocabulary for Distributed Coordination
Originated by GridWorks Energy Consulting

This specification defines the rules and registry model for Sema,
a versioned ontology expressed as JSON Schema for validating
serialized messages exchanged between independent applications.


## Table of Contents

- [Core Principles](#core-principles)
- [Specifications as Contracts](#specifications-as-contracts)
- [Registry Structure](#registry-structure)
- [Writing Vocabulary Files](#writing-vocabulary-files)
  - [Formats](#formats)
  - [Enums](#enums)
  - [Types](#types)
- [Reserved Namespaces](#reserved-namespaces)
- [Vocabulary Registration Process](#vocabulary-registration-process)
- [Governance](#governance)


## Core Principles

Sema defines how structured JSON messages declare and share meaning across independent systems.

The following principles apply to all Sema vocabulary definitions and all serialized messages validated under Sema.

**1. Vocabulary is Named** 

Every vocabulary component has a globally unique name using `left.right.dot` format. Names are not hierarchical inheritance; they are stable semantic identifiers.

Examples:
- Formats: `uuid4.str`, `utc.seconds`
- Enums: `base.g.node.class`, `gw1.unit` 
- Types: `bid`, `report`

These names are stable identifiers. They are used for validation, dependency tracking, and composition.

**2. Serialized Fields Use CamelCase** 

All serialized JSON field names MUST use CamelCase, recursively through nested structures.

```json
✅ Valid:
{"Bar": "bar", "TypeName": "foobar", "FooList": [{"Foo": "foo", TypeName: "foo"}]}

❌ Invalid (will be rejected, "foo" not CamelCase):  
{"Bar": "bar", "TypeName": "foobar", "FooList": [{"foo": "fools", TypeName: "foo"}]}
```

This ensures uniform structure across systems and prevents semantic drift caused by naming inconsistencies. It also helps signal Sema.

**2a. Primitive Types Are Validated at the Serialized Boundary**

Sema validation applies to the serialized JSON artifact as transmitted, not to a permissively coerced in-memory approximation.

If a schema says a value is an `integer`, then the serialized value MUST itself be an integer.

Implementations SHALL reject floats, strings, or other values that would only satisfy the schema after coercion or truncation.

**3. Types Declare Their Identity**:

Every type MUST include a TypeName field whose value equals the registered vocabulary name.

For versioned types, a `Version` field is also required

```json
✅ Valid example of a power.watts type:
{"Watts": 3723, "TypeName": "power.watts", "Version": "000"}

❌ Invalid
{"Watts": 3723}
```

Type identity is explicit. Messages are self-describing and machine-verifiable.

**4. Semantics at the Boundary Must Be Declared**

Sema is designed to make semantic meaning explicit at the serialization boundary.

If a semantic fact affects how a value is validated, transformed, composed, or interpreted across system boundaries, it SHALL be declared in the schema.

Meaning that influences interoperability SHALL NOT rely solely on:
 - Field names
 - Code conventions
 - Comments
 - External documentation

Instead, semantics that affect cross-system behavior must be structurally represented in the serialized contract.

For example, if two values must be compatible for composition, that compatibility must be declared in a way that can be validated mechanically. If a new semantic distinction is introduced, it requires a new version.

This design enables mechanical validation, safe composition, AI-assisted reasoning, and long-term interoperability without hidden assumptions.

Sema does not prescribe domain modeling style. It ensures that when semantics matter for distributed coordination, they are visible and verifiable in the serialized artifact itself.

**Vocabulary Scope and Adoption**

Registration in registry.yaml establishes uniqueness and governance — not universal adoption.

Publishing a vocabulary word does not imply that all Sema participants must or are expected to use it.

Vocabulary words are namespace-scoped. Organizations MAY and are encouraged to  define their own vocabularies under distinct namespaces (e.g., gw.*, acme.*, utilityX.*).

Universal adoption is determined by ecosystem coordination, not by registry presence.

## Specifications as Contracts

Sema vocabulary is defined through versioned JSON Schema documents written in YAML. Each schema serves as a contract defining structure, constraints, identity, ownership, and evolution.

These schemas collectively form a shared ontology: a governed vocabulary describing how independent systems represent and exchange meaning.

**Sema governs the structure and semantics of serialized JSON exchanged between independent applications.**
Validation applies to the concrete JSON artifacts that cross system boundaries — not merely to local type hints, IDE models, or in-memory representations.

Schemas are:
 - Machine-readable, human-readable and language-neutral
 - Versioned with controlled change
 - Dependency-tracked
 - Suitable for automated validation and code generation

They are transport-agnostic. Sema does not mandate HTTP, MQTT, WebSockets, or any specific runtime architecture. 

Systems may adopt Sema incrementally - as a single format, a single type, or an entire vocabulary tree. 

The goal is simple: shared meaning should be explicit and verifiable. Everything else builds on that.

For the purposes of immutability and version governance, a vocabulary definition is considered **published** when it is available at `https://schemas.electricity.works`.

Before publication, a schema MAY be revised in place to correct mistakes or to better align the initial Sema contract with demonstrated runtime behavior. After publication, historical versions are immutable and any semantic or validation change SHALL be expressed through a new version.

## Registry Structure

The `registry.yaml` file is the authoritative index of all Sema vocabulary components.  It defines:
 - What vocabulary words exist
 - Their ownership
 - Their versioning strategy
 - Their current latest version
 - Their dependency relationships

The registry is the canonical source of vocabulary identity and lifecycle state. 

Vocabulary components fall into three categories: **formats**, **enums** and **types**. 


### Top-Level Structure

1. The registry SHALL contain the following top-level sections in this order:

```
metadata:
formats:
enums:
types:

```

2. Entries within each section SHALL be listed in alphabetical order.

3. For versioned types, versions SHALL be listed in reverse chronological order (newest first).

### Metadata Block
```
metadata:
  registry_version: "1.0"
  last_updated: "2025-06-24T10:30:00Z"
  maintainer: "gridworks-energy"
```
 - `registry_version` - Version of the registry structure itself.
 - `last_updated` - RFC 3339 timestamp.
 - `maintainer` - Responsible organization.

All registry timestamps SHALL:

 - Conform to RFC 3339
 - Include full date and time components
 - Include seconds precision (HH:MM:SS)
 - Use UTC with the `Z` suffix
 - NOT include fractional seconds
 - Represent the publication time of the vocabulary entry in the registry.

Example:
```
  "2026-02-22T16:43:00Z"
```


### Registry Status Field

Registry entries (formats, enu8ms, types) MAY include a `status` field indicating lifecycle state.

Allowed values:
- `"draft"`: type is under active development and not yet stable
- `"active"`: type is stable and intended for production use (default if omitted)
- `"deprecated"`: type is no longer recommended for new use

If `status` is omitted, it SHALL be interpreted as `"active"`.


### Word Retirement (`replaced_by`)

A registry entry (format, enum, or type) MAY include a top-level `replaced_by` field naming another registry entry of the same kind that supersedes it.

```
<word-name>:
  ...
  replaced_by: <successor-word-name>
```

Rules:

- `replaced_by` is a registry-level retirement marker. The unit of retirement is the **word** (a registry entry), not a per-version, per-value, or per-attribute element.
- Per-version YAML schemas, individual enum values, and type properties are **immutable** and SHALL NOT carry their own `replaced_by` (or equivalent) marker.
- If `replaced_by` is present, the named successor SHALL exist as a registry entry of the same kind (format → format, enum → enum, type → type) and SHALL NOT itself be retired.
- A retired word's existing schemas remain valid for reading historical data; new producers SHOULD migrate to the successor.
- `replaced_by` MAY be combined with `status: "deprecated"`, but neither implies the other: `status` describes lifecycle stability, `replaced_by` names the migration target.


### Registry Format Entries

Formats are immutable and unversioned. Each format entry MUST include:

```
<format-name>:
  owner: <owner-id>
  schema_url: "https://schemas.electricity.works/formats/<format-name>"
  created: "<RFC 3339 timestamp>"
  description: "<concise structural description>"
```

For all vocabulary entries (formats, enums, and types), schema_url SHALL equal the $id declared in the referenced schema file.
For enums, the registry SHALL record top-level `enum_type`.
For enums, the registry MAY record top-level `value_type`.
If `value_type` is present, it SHALL be `"integer"` and the corresponding enum schema file SHALL have `type: integer`.
If `value_type` is omitted from an enum registry entry, it SHALL be interpreted as `"string"` and the corresponding enum schema file SHALL have `type: string`.
The enum schema file remains authoritative; the registry copy exists for compact tooling and validation.

Formats SHALL NOT include any version related information.

### Registry Enum Entries

Enums define closed sets of named values.

Enums MAY be either:

- `literal`: fixed and non-evolving  
- `versioned`: additive over time  

The `enum_type` field determines how the enum evolves.

---

**Literal Enum Structure**

For `literal` enums:

```
<enum-name>:
owner: <owner-id>
enum_type: "literal"
description: "<concise semantic description>"
value_type: "integer" # optional; omit for string-valued enums

schema_url: "https://schemas.electricity.works/enums/
<enum-name>/000"
created: "<RFC 3339 timestamp>"
```
**Literal Enum Field Requirements**

- `versions`
  - SHALL NOT be present

- `latest_version`
  - SHALL NOT be present

- `schema_url`
  - SHALL uniquely identify the enum schema  
  - SHALL include version `"000"`  

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC  

- `value_type`
  - MAY be present
  - if present, SHALL equal `"integer"`
  - if omitted, the enum SHALL be treated as string-valued


- Literal enums:
  - SHALL define a fixed set of values  
  - SHALL NOT add or remove values  


---

**Versioned Enum Structure**

For `versioned` enums:

```
<enum-name>:
latest_version: "<version>"
owner: <owner-id>
enum_type: "versioned"
description: "<concise semantic description>"
value_type: "integer" # optional; omit for string-valued enums

versions:
"<version>":
schema_url: "https://schemas.electricity.works/enums/
<enum-name>/<version>"
created: "<RFC 3339 timestamp>"
added_values:"<list of values added in this version>"
[..] # earlier versions
```


**Versioned Enum Field Requirements**

- `latest_version`
  - SHALL equal the highest version listed under `versions`

- `versions`
  - SHALL contain an entry for each published version  
  - SHALL be keyed by three-digit numeric strings  
  - SHALL be listed in decreasing order by version  

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC  

- `added_values`
  - SHALL be present for all versions except the initial version in the registry
  - SHALL be a list of enum values added in that version  

- `value_type`
  - MAY be present
  - if present, SHALL equal `"integer"`
  - if omitted, the enum SHALL be treated as string-valued



### Registry Type Entries

Each type entry in the registry SHALL declare a `versioning_strategy` and SHALL conform to one of the following models.

```
<type-name>:
  owner: <owner-id>
  versioning_strategy: "none" | "string" | "literal"
  description: "<concise semantic description>"
```


#### Versioning Semantics

**1. Versioned vs Versionless Types**
  - Types with `versioning_strategy: "none"` are **versionless**
  - Types with `versioning_strategy: "string"` or `"literal"` are **versioned**


**2. Versioned Types (`string` or `literal`)**

**2.1 Version Format**
  - Versions SHALL be **numeric strings of exactly three digits**
    
    Examples: `"000"`, `"001"`, `"013"`

**2.2 Ordering and Uniqueness** 
  - Each version SHALL be unique within the type
  - Each version entry SHALL include a `created` timestamp (see #### Version Updates)
  - The `created` timestamp SHALL be unique across all versions of the type
  - For any two versions `v_old` and `v_new`:
    - If `v_new` is numerically greater than `v_old`, then 
      `created(v_new)` SHALL be strictly later than `created(v_old)`
  - For any version entry `v`, `created(v)` SHALL be no earlier than the
    `created` timestamp of every vocabulary word named in that version's
    `direct_dependencies`

**2.3. Preferred Baseline Version**
  - `"000"` SHOULD be used as the initial version of a versioned type, but this is not required.

#### Versioned Type Structure

A versioned type entry SHALL include the following fields:

```
<type-name>:
  latest_version: "<version>"
  owner: <owner-id>
  versioning_strategy: "literal" | "string"
  description: "<concise semantic description>"

  versions:
    "<version>":
      schema_url: "https://schemas.electricity.works/types/<type-name>/<version>"
      created: "<RFC 3339 timestamp>"
      summary: "<concise description of change>"
      direct_dependencies:
        structural:
          - "<dependency>"
        axiom:
          - "<dependency>"
    [..] # earlier versions`

```

**Field Requirements**

  - `latest_version` 
    - SHALL equal the highest version listed under `versions`

  - `owner` 
    - SHALL reference a valid owner identifier defined in `owners.yaml`

  - `versions`
    - SHALL contain an entry for each published version of the type
    - SHALL be keyed by version string
    - SHALL be listed in decreasing order by version
    - The keys of `versions` SHALL match the `<version>` values used within each entry

**Version Entry Requirements**

Each entry under `versions` SHALL include:

- `schema_url`
  - SHALL uniquely identify the schema for that version

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC (e.g. `YYYY-MM-DDTHH:mm:ssZ`)

- `summary`
  - SHALL describe the change introduced in that version
  - SHALL conform to the rules defined in the Summary Field section

- `direct_dependencies`
  - SHALL conform to the rules defined in the Dependency Model section

#### Versionless Type Structure

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

**Field Requirements**
- `owner` 
  - SHALL reference a valid owner identifier defined in `owners.yaml`

- Versionless types SHALL NOT include a `versions` field

- `schema_url`
  - SHALL NOT include a version segment
  - SHALL uniquely identify the schema for the type

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC

- `direct_dependencies`
  - SHALL conform to the rules defined in the Dependency Model section


#### Strategy Semantics

The `literal` and `string` strategies differ only in schema validation behavior.

- `literal` enforces exact version matching in the schema
- `string` allows a schema to validate multiple versions

Both strategies:
- SHALL require all versions to be explicitly listed in the registry
- SHALL require versions to be strictly ordered
- SHALL require runtime upgrade chains to resolve messages to the latest version

#### Versioning Strategy Evolution

The `versioning_strategy` evolution through time for a type SHALL follow a monotonic strictness model:

```
none -> string -> literal
```

A type MAY transition only to a strictly more constrained strategy.

The following transitions are permitted:
- `none` → `string`
- `none` → `literal`
- `string` → `literal`

The following transitions are prohibited:
- `literal` → `string`
- `literal` → `none`
- `string` → `none`

Once a type adopts a stricter strategy, it SHALL NOT revert to a less strict strategy.

---

**Transition from Versionless to Versioned**

If a type with `versioning_strategy: "none"` adopts versioning:

- The registry SHALL be updated to reflect the new strategy
- A versioned lineage SHALL be established under `versions`
- The initial version SHOULD be `"000"`

A schema SHALL be published at:

```
https://schemas.electricity.works/types/
<type-name>/000
```


The following SHALL hold:

- The original versionless schema URL SHALL remain accessible  
- The original schema SHALL NOT be retroactively modified or assigned a version number  

Versioning begins at the point versioned schemas are introduced.

#### New Versions (Creation and Publication)

A new version of a versioned type SHALL be published when required and SHALL be recorded in the registry as defined below.

---

**1. When a New Version Is Required**

A new version SHALL be published if any of the following occur:

- A required property is added or removed  
- A property type or constraint changes  
- A referenced enum or type version changes  
- An axiom is added, removed, or modified  
- Validation constraints are strengthened or relaxed  
- Semantic meaning changes  

A new version SHOULD be published if:

- Property descriptions are clarified in a way that could affect interpretation  
- Architectural meaning changes in a non-trivial way  

A new version MAY be published for:

- Documentation or example improvements  

---

**2. Publishing a New Version**

When publishing a new version, the registry SHALL be updated as follows:

- A new entry SHALL be added under `versions` for the new version  

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
- latest_version SHALL be updated to the new version

```yaml
latest_version: "<new_version>"
```

**3. Preservation of Prior Versions**

 - All previously published versions SHALL remain listed in the registry
 - Previously published schema URLs SHALL remain accessible

Additional constraints on modification of prior versions are defined in the Immutability section.

#### Immutability

Sema registry entries are immutable except as explicitly permitted below.

Types with `status: "draft"` are exempt from the immutability requirements defined in this section.

---

**1. General Rules (All Types)**

- The schema referenced by `schema_url` SHALL NOT be modified in a way that changes validation behavior  
- Registry entries SHALL NOT be modified in a way that changes semantics  


---

**2. Versioned Types (Additional Constraints)**

- Version identifiers (the keys under `versions`) SHALL NOT be changed or removed
- New version identifiers MAY be added in accordance with the rules defined in **New Versions (Creation and Publication)**

---

**3. Permitted Changes (All Types)**

The following changes are permitted, provided they do not alter semantics:

- Correction of typographical errors  
- Clarification of descriptive text  

- Correction of `created` timestamps, provided that:
  - Timestamp uniqueness is preserved  
  - Timestamp ordering remains consistent with version ordering as defined in Versioning Semantics  

---
**4. Ownership Transfer**

The `owner` field MAY be updated to transfer ownership of a type, provided that:

- The transfer is explicitly authorized by the current owner  
- The new owner identifier is valid and defined in `owners.yaml`  
- The transfer does not alter the semantics of the type or any of its versions  

Ownership transfer SHALL NOT affect:
- Version history  
- Schema behavior  
- Dependency declarations  

Ownership transfer history is not tracked in the registry.

---
**5. Versionless Types**

Versionless types SHALL NOT be modified in a way that changes semantics.

If a semantic change is required the rules defined in **Versioning Strategy Evolution** SHALL be followed.


#### Dependency Model
Versioned types SHALL declare direct dependencies. These identify the Sema vocabulary required to 
  - validate the schema structurally 
  - implement any axioms attached to that specific type version

Dependencies are expressed in `registry.yaml` as:

```yaml
direct_dependencies:
  structural:
    - "<word-name>:<version>"   # enums or versioned types
    - "<word-name>"           # formats or versionless types
  axiom:
    - "<word-name>:<version>"
    - "<word-name>"
```


**1.Structural Dependencies**
  - SHALL include every vocabulary word explicitly referenced in the schema via `$ref` 
  - SHALL use the canonical identifier format:
    - `name:###` for enums and versioned types (3-digit numeric version)
    - `name` for formats and versionless types
  - SHALL NOT include transitive dependencies.

**2. Axiom Depenedencies**
  - SHALL include every Sema vocabulary word _not_ in the structural dependencies required to implement one or more axioms for that type version
  - SHALL be included even if the vocabulary is not referenced via $ref
  - SHALL use the same canonical identifier rules as `structural`
  - SHALL NOT include transitive dependencies.

**3. Structure and Ordering**
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
    - If structural dependencies exist but no axiom-level dependencies exist, `axiom` SHOULD be omitted.
    - If structural dependencies do not exist but axiom-level dependencies do exist, `structural` SHALL be declared as `[]`.

4. **Version Rules**
    - Versioned words MUST be referenced as `name:###` where `###` is a 3-digit numeric string.
    - Versionless words MUST NOT include a version suffix.
    - Mixing formats (e.g., including a colon for versionless words or omitting a version for versioned words) is invalid.

5. **Axiom Implementability**
    - Dependency declaration SHALL be sufficient to implement validation for the full contract of the type version, including its axioms.
    - If an axiom normatively names a specific Sema vocabulary word or version, that word SHALL appear in `axiom` unless it already appears in `structural`.
    - A type version SHALL NOT rely on undeclared external Sema vocabulary to make its axioms mechanically implementable.

### Change Process (Registry Updates)

All vocabulary changes SHALL be made through pull requests that:
 1. Update the relevant schema file
 2. Update registry.yaml
 3. Update dependencies (if applicable)
 4. Include a clear `summary` for new versions

For versioned types:

  - The `summary` SHALL describe the change relative to the previous version.
  - The `latest_version` field SHALL be updated.

Changes MUST pass:
 - Structural validation
 - Dependency validation
 - Registry consistency checks

### `owners.yaml` - Vocabulary Ownership Registry

The `owners.yaml` file defines the authoritative registry of vocabulary owners. Every vocabulary word in `registry.yaml` MUST reference an owner declared in `owners.yaml`.

Owner identifiers:
  - SHALL be lowercase kebab-case strings.
  - SHALL be globally unique within the registry.
  - SHALL remain stable once published.

Each owner entry SHALL include:

```
<owner-id>:
  contact: "<primary contact email or individual>"
  website: "<canonical public URL>"
  organization: "<legal or operating name>"
  description: "<concise description of domain or responsibility>"
```

- Owners are responsible for:
  - Maintaining schema documentation
  - Reviewing version changes
  - Coordinating breaking updates
  - Responding to dependency impacts

- Changing an owner of an existing vocabulary word SHALL require explicit review 

**Example** 

```yaml
gridworks-energy:
  contact: gridworks@gridworks-consulting.com
  website: https://electricity.works
  organization: "GridWorks Energy LLC"
  description: "Transactive energy infrastructure and thermal storage systems"

microerapower:  
  contact: Stephanie Benson <smb@microerapower.com>
  website: https://microerapower.com
  organization: "MicroEra Power"
  description: "Distributed energy resource management"
```

## Writing Vocabulary Files

### Formats

#### Purpose

Formats define reusable validation constraints for primitive values in Sema.

Formats are immutable vocabulary words that refine JSON primitive types (e.g., `string`, `integer`) with additional structural or semantic constraints.

Formats SHALL NOT reference other Sema vocabulary. 


#### Naming

 Format names SHALL use the `left.right.dot` convention.
 
 Examples:
  - `left.right.dot`
  - `uuid4.str`
  - `utc.seconds`


#### Schema Structure

Format schema files MUST include the following top-level fields:

```
$schema:
$id:
title:
description:
type:
<validation keywords>
examples:
counterexamples:
x-gridworks:
```

#### Required Top-Level Fields

  - `$schema` — MUST reference JSON Schema draft 2020-12.
  - `$id` — MUST be the canonical public schema URL.
  - `title` — MUST match the registered format name.
  - `description` — MUST describe structural meaning.
  - `type` — MUST be a JSON primitive (`string`, `integer`, `number`, or `boolean`).
  - `x-gridworks.owner` — MUST identify the owning organization.

#### Validation Constraints

Formats MAY use JSON Schema validation keywords appropriate to their primitive type, including:
  - `pattern`
  - `minimum`
  - `maximum`
  - `exclusiveMinimum`
  - `exclusiveMaximum`
  - `multipleOf`
  - `minLength`
  - `maxLength`

Formats SHALL NOT:
  - Use `$ref`
  - Reference other Sema vocabulary
  - Include a `Version` field
  - Include `additionalProperties`
  - Declare `required`

When declaring regular expression patterns in YAML schema files, the pattern value SHALL be quoted as a string.

This prevents YAML parsing ambiguities and ensures consistent interpretation of escape sequences. Double-quoted strings SHOULD be used, with backslashes escaped appropriately (e.g., "\\." for a literal dot).

#### Immutability

Formats are immutable once registered. 

The validation pattern, constraints, and semantics of a format SHALL NOT change after publication.  

Formats do not have versions.


#### Examples and Counterexamples 
Format schemas SHOULD include:
  - `examples` — Valid representative values
  - `counterexamples` — Explicit invalid values with short inline explanations

Examples and counterexamples improve mechanical validation testing and IDE support.



#### Example: `utc.milliseconds` (Format)
```
# formats/utc.milliseconds.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/formats/utc.milliseconds"

title: "utc.milliseconds"
description: |
  UTC timestamp expressed as milliseconds since Unix epoch
  (1970-01-01T00:00:00Z). Must be an integer between
  2000-01-01T00:00:00Z and 3000-01-01T00:00:00Z inclusive.
  
type: integer
minimum: 946684800000
maximum: 32503680000000

examples:
  - 1609459200000  
  - 1609459200500
  - 1735689600123

counterexamples:
  - 0      
  - 946684799999
  - 32503680000001
  - 1609459200.5

x-gridworks:
  owner: "gridworks-energy"
```

### Enum Schema Files

#### Purpose

Enum schema files define the allowed values for a single enum version.

Each schema constrains a value to a closed set of string literals.

---

#### Naming

Enum names SHALL use the `left.right.dot` convention.

Examples:
  - `base.g.node.class`
  - `sh.actor.role`
  - `market.quantity.unit`

---

#### Schema Structure

Each enum schema file SHALL define exactly one enum version.

Schema files MUST include:

```
$schema:
$id:
title:
type: "string" | "integer"
description:
enum:
default:
x-gridworks:
```

---

#### Required Fields

- `$schema`
  - SHALL reference JSON Schema draft 2020-12

- `$id`
  - SHALL equal the canonical schema URL
  - SHALL match the corresponding `schema_url` in `registry.yaml`

- `title`
  - SHALL equal the enum name

- `type`
  - SHALL be `"string"` or `"integer"`
  - SHALL be `"integer"` if and only if the corresponding enum registry entry has `value_type: "integer"`
  - SHALL be `"string"` if the corresponding enum registry entry omits `value_type`

- `description`
  - SHALL describe the semantic role of the enum

- `enum`
  - SHALL list all allowed values for this version

- `default`
  - SHALL be one of the declared enum values

---

#### x-gridworks Metadata

Each enum schema SHALL include:

```
x-gridworks:
owner: "<owner-id>"
version: "<3-digit version>"
```


**Requirements**

- `owner`
  - SHALL match the owner declared in `registry.yaml`

- `version`
  - SHALL be a three-digit numeric string
  - SHALL match the version encoded in `$id`

---

#### Optional Metadata

```
x-gridworks:
  value_descriptions:
"<EnumValue>": "<Description>"

x-gridworks:
  extended_description: >
...
```


**Rules**

- `value_descriptions`
  - MAY appear only within `x-gridworks`
  - SHOULD include an entry for each enum value
  - SHOULD describe semantic meaning, not restate the name

- `extended_description`
  - MAY appear only within `x-gridworks`
  - MAY provide architectural or contextual explanation
  - MUST NOT introduce new normative constraints
  - MUST NOT change the meaning of any enum value

---

#### Forbidden Extra Fields

Enum schema files SHALL NOT include any top-level fields other than:

- `$schema`
- `$id`
- `title`
- `type`
- `description`
- `enum`
- `default`
- `x-gridworks`

Within `x-gridworks`, enum schema files SHALL NOT include any fields other than:

- `owner`
- `version`
- `value_descriptions`
- `extended_description`

---

#### Evolution Rules

Enum evolution is determined by `enum_type`.

- `literal`
  - SHALL have version `"000"`
  - SHALL define a fixed set of values
  - SHALL NOT add, remove, reorder, or reinterpret values
  - SHALL NOT change the default

- `versioned`
  - Each schema file defines a single version
  - New versions MAY append values to the end of the `enum` list
  - Values present in prior versions SHALL appear in the same relative order
  - SHALL NOT remove or reorder existing values
  - SHALL NOT change the semantic meaning of existing values
  - SHALL NOT change the default

---

#### Description Evolution

In new versions of a `versioned` enum, the following MAY be updated:

- `description`
- `value_descriptions`
- `extended_description`

Such updates:

- MUST NOT change semantic meaning
- MUST NOT reinterpret prior behavior
- MUST NOT introduce new normative constraints

If semantic meaning changes, a new enum value MUST be introduced instead.



#### Example: `base.g.node.class v000` (Enum)

```
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/enums/base.g.node.class/000"

title: "base.g.node.class"
type: "string"
description: >
  Ontology classification for Grid Nodes (GNodes) used to describe their
  structural relationship to the physical electric grid. Values identify
  whether a node represents a physical metered boundary, a physical
  topological structure, a market coordination constraint, or a purely
  logical entity.

  Every GNode SHALL declare exactly one base.g.node.class value.

enum:
  - "TerminalAsset"
  - "LeafTransactiveNode"
  - "ConnectivityNode"
  - "MarketMaker"
  - "Logical"

default: "Logical"

x-gridworks:
  owner: "gridworks-energy"
  version: "000"
  value_descriptions:
    "TerminalAsset": >
      A physical transactive asset such as a heat pump, hot water heater, residential battery, 
      electric vehicle, or any other end-use device located behind an atomic metered point.
    
    "LeafTransactiveNode": >
      The atomic metered unit of the grid. Represents the smallest indivisible metering
      boundary capable of participating in markets or entering Dispatch Contracts on
      behalf of a TerminalAsset. Every TerminalAsset is associated with exactly one
      LeafTransactiveNode.

    "ConnectivityNode": >
      A physical topological node in the electric power system where conductors join,
      split, or change configuration. Conceptually aligned with the ConnectivityNode
      in the IEC 61970/61968 CIM (Common Information Model), but simplified for
      distribution-level modeling and OPF applications.

    "MarketMaker": >
      A physical constraint point in the conductor topology that requires localized market
      coordination. Identified as a grid location (e.g., feeder constraint, transformer limit)
      where a MarketMaker actor computes local prices for balancing and constraint compliance.
      See [market-maker](https://gridworks.readthedocs.io/en/latest/market-maker.html).

    "Logical": >
      A non-physical Grid Node whose identity carries no inherent conductor-topology or
      metering semantics. Used for purely logical or service-level nodes such as SCADA,
      forecasting services, market-maker actors, simulation nodes, or organizational
      microservices. Logical nodes may coordinate with or operate on physical nodes, but do
      not themselves represent physical grid structure.

```

### Types

#### Purpose

Types define structured, versioned semantic contracts in Sema.

Types may reference:

 - Formats
 - Enums
 - Other versioned Sema types

Types are what get serialized/deserialized and sent between applications. They are the primary building block of Sema.

#### Identity Fields

All versioned types SHALL explicitly declare both:
  - `TypeName`
  - `Version` (if `versioning_strategy` is not `none`)

**TypeName**
  - MUST be present in properties
  - MUST be declared using const
  - MUST match the vocabulary name registered in registry.yaml

Example:
```
TypeName:
  const: "bid"
```

**Versions**
 - MUST follow the rules defined by versioning_strategs. See section XX


#### Version Strategy Semantics
Versioned types (`string` and `literal`) SHALL:
- Enumerate all versions explicitly in the registry
- Maintain strict version ordering
- Provide upgrade paths between versions

#### Required Top-Level Order
Named type schemas SHALL appear in the following order:

```
$schema:
$id:
title:
type:
description:
properties:
required:
additionalProperties:
examples:  # Optional
x-gridworks:

```

#### Schema Header Requirements

 - `$schema` MUST reference JSON Schema draft 2020-12
 - `$id` MUST be the canonical public schema URL
 - `title` MUST match the vocabulary name registered in `registry.yaml`
 - `description` MUST describe structural meaning

 #### Property Definitions

 Each property SHALL include:
   - `$ref` or `type`
and MAY include
   - `description`

Property descriptions are **strongly recommended** but not required. If provided, descriptions SHOULD be complete sentences, describe semantic meaning, avoid implementation details.  

Over time, high-value types SHOULD include complete property descriptions.

Type properties MAY use any applicable JSON Schema validation keywords (e.g., minLength, maxLength, minimum, pattern, minItems) provided they do not contradict declared axioms.

#### Referencing Other Vocabulary

**Format references:**
```yaml
properties:
  NodeId:
    $ref: "https://schemas.electricity.works/formats/uuid4.str"
```

**Enum references:**
```yaml
properties:
  ActorRole:
    $ref: "https://schemas.electricity.works/enums/sh.actor.role/000"
```

**Type references:**  
```yaml
properties:
  ChannelReadings:
    type: array
    items:
      $ref: "https://schemas.electricity.works/types/channel.readings/002"
```


#### Required Property Declarations
All required declarations MUST be explicitly listed under `required`. 

#### `additionalProperties` Rule

The preferred default for Sema types is 

```
additionalProperties: false
```

This prevents unintended schema drift and enforces explicit semantic contracts.

However, types under active schema evolution, or types that serve as flexible
aggregation or embedding layers, MAY declare:

```
additionalProperties: true
```
Such types MUST document this behavior in their description or
extended_description, including the intended purpose of additional fields.

Over time, as schemas stabilize, types SHOULD transition toward:


```
additionalProperties: false
```


#### Examples (Optional)
Types MAY include an examples field.

If present:
  - Examples SHALL be serialized JSON documents, not YAML object representations
  - Examples SHALL be structurally valid according to the schema.
  - Examples SHOULD represent the smallest semantically valid instance of the type (minimal canonical example).
  - Examples MAY include a realistic instance in addition to the minimal example.
  - Examples MUST NOT contradict any declared axioms.

Examples serve as:
  - Developer guidance
  - IDE assistance
  - Validation fixtures
  - Contract clarity for integrators

Example structure:
```examples:
  - |
    {
      "TypeName": "example.type",
      "Version": "000",
      ...
    }

```

Examples are optional but strongly recommended for public-facing types and core system messages.

#### x-gridworks Metadata

All schemas MUST include:
```
x-gridworks:
  owner: "<owner-id>"
```

Optional fields include `axioms` and `extended_description`.

Within x-gridworks, fields SHALL appear in the following order when present: owner, supersedes (if applicable), axioms (if any), extended_description (if any).


#### Axioms

Axioms describe semantic invariants that cannot be expressed through structural JSON Schema constraints.

Each axiom SHALL:

- Be numbered using positive integers starting at 1 (1, 2, 3, …).
- Appear in ascending numeric order.
- Use normative language (SHALL, MUST).
- Not restate structural constraints already enforced by the schema.
- Be specific to a particular TypeName + Version.

Axiom numbering is scoped to a specific type version. When a new version of a type is created, axioms MAY be renumbered starting at 1.

In YAML, axioms SHALL be represented under `x-gridworks.axioms`
as an ordered list. Each axiom entry SHALL include:

- `number`: integer number
- `name`: short identifier
- `statement`: normative statement

Example:

x-gridworks:
  axioms:
    - number: 1
      name: "NonEmptyLists"
      statement: "ValueList and ScadaReadTimeUnixMsList SHALL be non-empty."
    - number: 2
      name: "ListLengthConsistency"
      statement: "len(ValueList) SHALL equal len(ScadaReadTimeUnixMsList)."

SDK implementations SHOULD provide one validation function per axiom.
In the Python SDK, validator functions SHALL be named:

    check_axiom_<n>

where <n> is the axiom number.

#### `extended_description`

`extended_description` provides architectural context, rationale and
system-level explanation. It SHALL NOT duplicate `description`

#### SDK Implementations and Non-Serialized Extensions

Sema defines the structure and semantics of serialized JSON exchanged between independent applications. SDK implementations MAY provide additional computed properties, helper methods, validation utilities, or convenience accessors that are not present in the serialized schema.

Such extensions:

  - SHALL NOT alter or extend the serialized contract.
  - SHALL NOT introduce additional serialized fields unless explicitly defined in the schema.
  - SHALL NOT modify validation behavior defined by the schema and axioms.

These implementation-level conveniences are language-specific and are not considered part of the Sema vocabulary.

#### Example: `bid v000` (Type)

```
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/types/bid/000"

title: "bid"
type: object
description: >
  A market-normalized, slot-specific price–quantity schedule submitted by a
  market participant. A bid expresses willingness to inject or withdraw a
  quantity of a market-defined commodity as a function of price, subject to
  the rules of the MarketType associated with the specified MarketSlot.

  Bids are economically admissible, cryptographically anchored messages that
  serve as the primary input to market aggregation and clearing. Differences
  between participant classes (e.g. leaf nodes, aggregators, fleets, generators)
  are expressed through MarketType rules and bidder authorization registries,
  not through differences in bid structure.

properties:
  BidderAlias:
    $ref: "https://schemas.electricity.works/formats/left.right.dot"
    description: >
      Canonical alias of the market participant submitting this bid. This alias
      is used to associate the bid with authorization, fee-payment credentials,
      and market participation rules defined outside this message.

  MarketSlotName:
    $ref: "https://schemas.electricity.works/formats/market.slot.name"
    description: >
      Identifier of the market slot for which this bid applies. The MarketSlot
      determines the applicable MarketType, settlement interval, and market
      rules used to validate and clear the bid.

  PqPairs:
    type: array
    items:
      $ref: "https://schemas.electricity.works/types/price.quantity.unitless/000"
    description: >
      Ordered list of price–quantity pairs defining the bid curve. Prices SHALL
      be ordered according to MarketType rules and normalized to the market’s
      declared price domain. Quantities represent willingness to inject or
      withdraw at the corresponding prices.
    minItems: 1

  InjectionIsPositive:
    type: boolean
    description: >
      Sign convention for quantities in this bid. If true, positive quantities
      represent injection into the market; if false, positive quantities
      represent withdrawal. The interpretation of this convention is governed
      by the associated MarketType.

  PriceUnit:
    $ref: "https://schemas.electricity.works/enums/market.price.unit/000"
    description: >
      Unit of the price axis for this bid. MUST match the PriceUnit declared by
      the MarketType associated with the MarketSlot.

  QuantityUnit:
    $ref: "https://schemas.electricity.works/enums/market.quantity.unit/000"
    description: >
      Unit of the quantity axis for this bid. MUST match the QuantityUnit
      declared by the MarketType associated with the MarketSlot.

  SignedMarketFeeTxn:
    type: string
    description: >
      Cryptographic proof of payment of the market-defined bid submission fee.
      This value SHALL reference a signed transaction that satisfies the
      market’s fee and admission rules for the specified MarketSlot.

      The SignedMarketFeeTxn proves economic admissibility of the bid. It does
      NOT, by itself, prove physical feasibility, delivery capability,
      portfolio composition, or settlement commitment. Those guarantees, if
      any, are established by clearing, dispatch, and settlement processes
      external to this message.

  # Identity Fields
  TypeName:
    const: "bid"

  Version:
    const: "000"

required:
  - BidderAlias
  - MarketSlotName
  - PqPairs
  - InjectionIsPositive
  - PriceUnit
  - QuantityUnit
  - SignedMarketFeeTxn
  - TypeName
  - Version

additionalProperties: false

x-gridworks:
  owner: "gridworks-energy"

  axioms:
    - number: 1
      name: "MarketNormalizationAnchor"
      statement: >
        The price of the first element in PqPairs SHALL equal the PriceMax
        defined by the MarketType associated with MarketSlotName.

    - number: 2
      name: "UnitConsistency"
      statement: >
        PriceUnit and QuantityUnit SHALL match the units declared by the
        MarketType associated with MarketSlotName.

    - number: 3
      name: "CurveAdmissibility"
      statement: >
        The structure, ordering, and cardinality of PqPairs SHALL conform to
        the admissibility rules of the MarketType associated with MarketSlotName
        (including any constraints on price ordering, monotonicity, tick size,
        or maximum number of segments).

    - number: 4
      name: "EconomicAdmission"
      statement: >
        SignedMarketFeeTxn MUST be verifiable under the market’s fee and
        admission policy for the specified MarketSlot.
  
  extended_description: >
    The bid type is the foundational economic message of the GridWorks market
    architecture. By enforcing strict normalization against MarketType-defined
    price and quantity domains, bids enable a self-scaling market maker
    strategy in which aggregation, clearing, and dispatch logic can be applied
    uniformly across participant classes and market layers.

    All bids share a common structure and validation contract. Differences in
    physical assets, aggregation scope, or operational responsibility are
    expressed through external registries, MarketType definitions, and
    settlement processes rather than through specialized bid schemas.

    This design supports permissioned or permissionless participation,
    economic rate-limiting via fees, and bounded computational complexity,
    while preserving extensibility for future market products and clearing
    mechanisms.
```

#### Example: `report v002` (Type)

```
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.electricity.works/types/report/002"

title: "report"
type: object
description: >
  Primary telemetry and state reporting message produced by a SCADA node
  for a specific reporting slot. A report contains all meaningful channel
  readings, state transitions, and FSM outputs observed during the slot
  period.

properties:

  FromGNodeAlias:
    $ref: "https://schemas.electricity.works/formats/left.right.dot"
    description: >
      GNode alias of the entity sending this report.

  FromGNodeInstanceId:
    $ref: "https://schemas.electricity.works/formats/uuid4.str"
    description: >
      Unique identifier of the specific runtime instance producing this report.

  AboutGNodeAlias:
    $ref: "https://schemas.electricity.works/formats/left.right.dot"
    description: >
      GNode alias of the entity about which this report is describing telemetry.

  SlotStartUnixS:
    $ref: "https://schemas.electricity.works/formats/utc.seconds"
    description: >
      Start time of the reporting period in Unix seconds.

  SlotDurationS:
    type: integer
    minimum: 1
    description: >
      Duration of the reporting slot in seconds.

  ChannelReadingList:
    type: array
    description: >
      Telemetry readings observed during this reporting slot.
    items:
      $ref: "https://schemas.electricity.works/types/channel.readings/002"

  StateList:
    type: array
    description: >
      State transitions observed during this reporting slot.
    items:
      $ref: "https://schemas.electricity.works/types/machine.states/000"

  FsmReportList:
    type: array
    description: >
      Finite state machine reports generated during this slot.
    items:
      $ref: "https://schemas.electricity.works/types/fsm.full.report/001"

  MessageCreatedMs:
    $ref: "https://schemas.electricity.works/formats/utc.milliseconds"
    description: >
      Timestamp at which this report was created by the reporting node.

  Id:
    $ref: "https://schemas.electricity.works/formats/uuid4.str"
    description: >
      Globally unique identifier for this report message.

  TypeName:
    const: "report"

  Version:
    const: "003"

required:
  - FromGNodeAlias
  - FromGNodeInstanceId
  - AboutGNodeAlias
  - SlotStartUnixS
  - SlotDurationS
  - ChannelReadingList
  - StateList
  - FsmReportList
  - MessageCreatedMs
  - Id
  - TypeName
  - Version

additionalProperties: false

examples:
  - |
    {
      "FromGNodeAlias": "hw1.isone.me.versant.keene.beech.scada",
      "FromGNodeInstanceId": "19ee09df-80ba-437b-b6c1-1eebe9d34801",
      "AboutGNodeAlias": "hw1.isone.me.versant.keene.beech.ta",
      "SlotStartUnixS": 1762633800,
      "SlotDurationS": 300,
      "ChannelReadingList": [{
              "ChannelName": "hp-lwt",
              "ValueList": [
                  19900,
                  19700
              ],
              "ScadaReadTimeUnixMsList": [
                  1762633800195,
                  1762634056082
              ],
              "TypeName": "channel.readings",
              "Version": "002"
          }],
      "StateList": [{
              "MachineHandle": "ltn.la.relay6",
              "StateEnum": "relay.closed.or.open",
              "StateList": [
                  "RelayOpen"
              ],
              "UnixMsList": [
                  1762634098098
              ],
              "TypeName": "machine.states",
              "Version": "000"
          }],
      "FsmReportList": [],
      "MessageCreatedMs": 1762634100033,
      "Id": "7499defd-c54a-4061-a37a-17f3c84f88a2",
      "TypeName": "report",
      "Version": "002"
    } 

x-gridworks:
  owner: "gridworks-energy"
  extended_description: >
    Reports are sent at fixed slot intervals (typically 5 minutes) and
    provide a durable historical record of telemetry and state changes
    observed during that period.

    GridWorks SCADA devices emit most channel readings asynchronously
    when values change beyond configured thresholds. Each reading is
    timestamped at the moment of observation by the SCADA device.
    Reports preserve these original timestamps without resampling
    or aggregation.

    As a result, a report represents a batched event log for the slot
    period rather than a sampled snapshot. Consumers can reconstruct
    the precise timing of state transitions (e.g., relay changes)
    and value updates within the slot window.

    This differs from snapshot messages, which represent the most recent
    value of each channel at a single point in time and are optimized
    for near-real-time visualization rather than historical accuracy.
```

## Reserved Namespaces
Certain top-level namespace prefixes MAY be reserved in the future to support cross-cutting behavior, forward compatibility, or governance coordination.

At present, no namespace prefixes are formally reserved.

As ecosystem experience grows, reserved namespaces — if introduced — SHALL be documented in this section and applied prospectively. Previously registered vocabulary SHALL NOT be retroactively restricted.

Namespace reservation is expected to be rare and justified by clear interoperability requirements.

## Vocabulary Registration Process

 You can certainly use these ideas on your own within your organization (or fork this repo). If you are in the electric grid balancing eco-system, we strongly encourage you to contribute your words to Sema.

### How to Add New Vocabulary

1. **Search existing vocabulary** - Check [registry.yaml](type_definitions/registry.yaml) to make sure nobody owns this word yet
2. **Fork and create PR** - Add yourself to [owners.yaml](type_definitions/owners.yaml) and update [registry.yaml](type_definitions/registry.yaml) with your new vocabulary
3. **Send us an email** - Let us know at gridworks@gridworks-consulting.com



## Governance

This document defines the structural and evolutionary rules of Sema.

When conflicts arise between implementation and specification:
  - The specification governs.
  - Implementations SHALL be corrected.

### Ownership Responsibilities

Each vocabulary word declared in `registry.yaml` SHALL have exactly one owner listed in `owners.yaml`.

Owners are responsible for:
 - Maintaining schema correctness and documentation
 - Reviewing and approving version changes
 - Ensuring evolution rules are followed
 - Coordinating dependency impacts when introducing new versions
 - Responding to reasonable community questions regarding semantics

Owners SHALL NOT:
 - Publish breaking changes without incrementing version
 - Modify historical versions in ways that alter validation behavior
 - Transfer ownership without registry update

### Vocabulary Naming Discipline

Sema supports a federated vocabulary model. Registration establishes uniqueness and governance — not universal adoption.

Owners SHALL select names that reflect clear semantic intent and avoid collision with common primitives (e.g., uuid, id, value). Namespace scope signals ownership, not ecosystem authority.

This principle is especially important for enums, which define semantic taxonomies.  Organization-specific taxonomies SHOULD be published under organization-scoped prefixes (e.g. `gw.g.node.class`)

The registry maintainer MAY request renaming prior to publication to prevent excessive namespace capture or long-term ambiguity.

### Change Process

All vocabulary changes SHALL be made through pull requests that:
 1. Update the relevant schema file
 2. Update registry.yaml
 3. Update dependencies (if applicable)
 4. Include a clear `summary` for new versions

For versioned types:

  - The `summary` SHALL describe the change relative to the previous version.
  - The `latest_version` field SHALL be updated.

Changes MUST pass:
 - Structural validation
 - Dependency validation
 - Registry consistency checks

### Conflict Resolution

If ambiguity or dispute arises regarding:
 - Semantic interpretation
 - Versioning requirements
 - Dependency correctness

The resolution order SHALL be:
  1. The schema file for the relevant version
  2. `registry.yaml`
  3. This document


Schema validation behavior always governs runtime correctness.
Registry metadata governs lifecycle and discovery.
