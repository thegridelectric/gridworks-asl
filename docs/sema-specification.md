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


### Format Entries

Formats are immutable and unversioned. Each format entry MUST include:

```
<format-name>:
  owner: <owner-id>
  schema_url: "https://schemas.electricity.works/formats/<format-name>"
  created: "<RFC 3339 timestamp>"
  description: "<concise structural description>"
```

For all vocabulary entries (formats, enums, and types), schema_url SHALL equal the $id declared in the referenced schema file.

Formats SHALL NOT include any version related information.

### Enum Entries
Enums are versioned and additive.

Each enum entry MUST include:

```
<enum-name>:
  latest_version: "001"
  owner: <owner-id>
  description: "<concise semantic description>"

  versions:
    "001":
      schema_url: "https://schemas.electricity.works/enums/<enum-name>/001"
      created: "<RFC 3339 timestamp>"
    "000":
      schema_url: "https://schemas.electricity.works/enums/<enum-name>/000"
      created: "<RFC 3339 timestamp>"
```

Enum versions: 
  - MUST be three-digit numeric strings.
  - MAY add values.
  - SHALL NOT remove existing values.

### Type Entries

Types may use one of three versioning strategies. 

What the Registry should look like
**Versioned Type (`literal` or `string`)**

```
<type-name>:
  latest_version: "200"
  owner: <owner-id>
  versioning_strategy: "literal"  # "none", "literal", or "string"
  description: "<concise description>"

  versions:
    "<latest_version>":
      schema_url: "https://schemas.electricity.works/types/<type-name>/<latest_version>"
      created: "<RFC 3339 timestamp>"
      summary: "<concise description of change>"
      dependencies:
        direct: 
         - "sh.actor.class:000"
         - "spaceheat.name:000"
        all: 
         - "sh.actor.class:000"
         - "spaceheat.name:000"
    [..] # earlier versions

```

**Versionless type (`none`)**
```
<type-name>:
  owner: <owner-id>
  versioning_strategy: "none"
  description: "<concise description>"

  schema_url: "https://schemas.electricity.works/types/<type-name>"
  created: "<RFC 3339 timestamp>"
  summary: "<concise description of change>"
  dependencies:
    direct:
      - "uuid4.str"
    all:
      - "uuid4.str"
  ```

#### Version Updates

When publishing a new version of a versioned type, the registry SHALL be updated as follows:

**1. Add a New Version Entry**

New versions SHALL be larger numbers, and listed in reverse order

```
versions:
  "004":
    schema_url: "https://schemas.electricity.works/types/<type-name>/004"
    created: "<RFC 3339 timestamp>"
    summary: "<concise description of change>"
    dependencies:
      direct:
        - ...
      all:
        - ...
```


**2. Update `latest_version`**
```
latest_version: "004"
```

**3. Preserve Prior Versions**
 - All previously published versions SHALL remain listed.
 - Prior version metadata SHALL NOT be modified except to correct typographical errors.
 - Dependencies for prior versions MUST NOT be retroactively changed.
 - Previously published schema URLs MUST remain accessible.

#### Summary Field

Each version entry SHOULD include a `summary` field describing the primary change introduced in that version.

Rules:
  - The summary SHALL be concise.
  - The summary SHALL describe what changed relative to the immediately previous version.
  - The summary SHALL NOT duplicate the full schema description.
  - The summary SHALL NOT reinterpret prior semantics.
  - The summary exists for governance clarity and tooling support; it does not affect validation.

#### When a New Version Is Required

A new version SHALL be published if any of the following occur:
  - A required property is added or removed.
  - A property type or constraint changes.
  - A referenced enum or type version changes.
  - An axiom is added, removed, or modified.
  - Validation constraints are strengthened or relaxed.
  - Semantic meaning changes.

A new version SHOULD be published if:
  - Property descriptions are clarified in a way that could affect interpretation.
  - Architectural meaning changes in a non-trivial way.

A new version MAY be published for documentation or example improvements.

#### Versioning Strategy Evolution

The versioning_strategy for a type SHALL follow a monotonic strictness model:

```
none  →  string  →  literal
```

The following transitions are permitted:
 - `none` → `string`
 - `none` → `literal`
 - `string` → `literal`

The following transitions are prohibited:
 - `literal` → `string`
 - `literal` → `none`
 - `string` → `none`

Once a type adopts a stricter versioning strategy, it SHALL NOT revert to a less strict strategy.

#### Transition from Versionless to Versioned

If a type originally used versioning_strategy: none and later adopts versioning:
 - The registry SHALL be updated to reflect the new versioning strategy.
 - A new versioned lineage SHOULD begin at "000".
 - A schema SHALL be published at:

```
https://schemas.electricity.works/types/<type-name>/000
```

  - The original versionless schema URL SHALL remain accessible.
  - The original schema SHALL NOT be retroactively modified or assigned a version number.

Versioning begins at the moment versioned schemas are introduced.

#### Prohibited Changes

For versioned types:
  - `versioning_strategy` MUST NOT change in a way that reduces strictness.
  - Previously published versions MUST NOT be removed.
  - Historical schemas MUST NOT be altered in ways that change validation behavior.

### Dependency Model
Versioned types SHALL declare dependencies. Dependencies describe other Sema vocabulary words (types, enums, or formats) referenced by the schema.

Dependencies are expressed as two ordered lists:

dependencies:
  direct:
    - "<word-name>:<version>"   # for versioned types or enums
    - "<format-name>"           # for versionless formats
  all:
    - "<word-name>:<version>"
    - "<format-name>"

**Rules**

1. **direct**
    - SHALL include every vocabulary word explicitly referenced in the schema via `$ref` (all formats, enums, and types).
    - SHALL use the canonical identifier format:
      - `name:###` for versioned types and enums (3-digit numeric version)
      - `name` for versionless formats or versionless types
    - SHALL NOT include transitive dependencies.

2. **all**
    - SHALL include the full transitive closure of direct.
    - SHALL be a strict superset or equal to direct.

3. **Ordering and Structure**
    - Both `direct` and `all` SHALL:
      - Be alphabetically sorted (lexicographically by full identifier string)
      - Contain no duplicates
      - Be declared as block lists (one entry per line)
    - Dependency references SHALL NOT include URL prefixes or file paths.
    - When computing dependencies, tooling SHALL extract the vocabulary word from the $ref URL path and omit the domain prefix.
    - If no dependencies exist, both lists SHALL be explicitly declared as empty:
```
dependencies:
  direct: []
  all: []
```

4. **Version Rules**
    - Versioned words MUST be referenced as `name:###` where `###` is a 3-digit numeric string.
    - Versionless words MUST NOT include a version suffix.
    - Mixing formats (e.g., including a colon for versionless words or omitting a version for versioned words) is invalid.


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

### Enums

#### Purpose

Enums define controlled vocabularies for semantic categories within Sema. Each enum constrains a value to a closed set of string literals.

#### Naming

Enum names SHALL use the `left.right.dot` convention.

Examples:
  - `base.g.node.class`
  - `sh.actor.role`
  - `market.quantity.unit`

#### Schema Structure

Enum schema files MUST include:

```
$schema:
$id:
title:
type: "string"
description:
enum:
default:
x-gridworks:
```

#### Required Top-Level Fields
 - `$schema` — MUST reference JSON Schema draft 2020-12.
 - `$id` — MUST be the canonical public schema URL.
 - `title` — MUST match the registered enum name.
 - `type` — MUST be "string".
 - `description` — MUST describe the semantic role of the enum.
 - `enum` — MUST list all allowed string values.
 - `default` — MUST equal one of the declared enum value.


#### x-gridworks Metadata

The `x-gridworks` block MUST include:
```
x-gridworks:
  owner: "<owner-id>"
  version: "<3-digit version>"
```

Optional: 
```
value_descriptions:
  "<EnumValue>": "<Description>"
```

If value_descriptions is provided:
  - Every enum value SHOULD have a description.
  - Descriptions SHOULD explain semantic meaning, not restate the name.


#### Evolution Rules

Enums are versioned. These versions SHALL match the pattern `000`, `001`, `002` etc (i.e. three-digit numeric strings). For enums, these
versions SHALL increase with each published version. 

New versions MAY append new values to the end of the `enum` list. New versions SHALL NOT
  - Remove existing values
  - Reorder existing values
  - Change the semantic meaning of existing values
  - Change the `default` value

####  Description Evolution

In new enum versions, the following MAY be modified for clarity:
  - description
  - value_descriptions

Such modifications:
  - MUST NOT change the semantic meaning of any enum value
  - MUST NOT reinterpret prior behavior
  - MUST NOT introduce new normative constraints


Description updates SHALL be limited to:
  - Clarifying intent
  - Improving wording
  - Correcting grammar or typographical errors
  - Expanding architectural explanation without altering semantics

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

**Version**
 - MUST follow the rules defined by versioning_strategy

#### Versioning Model

Types may use one of three `versioning_strategy` values in `registry.yaml`:
 - `none`
 - `literal`
 - `string`

The `string` strategy means one schema file can validate multiple versions, and allows for a softer handling of backwards compatibility.  Under string, the registry SHALL list only one schema file. The schema SHALL internally validate the Version property.

**Strategy:** `none`

Types with strategy `none`:
 - MUST NOT include a Version field in the schema.

**Strategy:**  `literal`

  - MUST include a `Version` field in the schema.
  - The `Version` property must be `const "<3-digit>".
  - For `literal`:
    -  The `Version field MUST be defined using `const`

**Strategy:**  `string`

  - For `string`: 
    - The `Version field MUST be declared as a `string`


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
      $ref: "https://schemas.electricity.works/types/fsm.full.report/000"

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
    const: "002"

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
              "MachineHandle": "a.aa.relay6",
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
