# Authoring — Enum Schema Files

This sub-spec covers writing enum schema files (the YAML in
`definitions/enums/`). For the `registry.yaml` entry shape, see
[../registry/enums.md](../registry/enums.md).

Read [../primary.md](../primary.md) for core principles.

## Purpose

Enum schema files define the allowed values for a single enum version.
Each schema constrains a value to a closed set of string (or integer)
literals.

## Naming

Enum names SHALL use the `left.right.dot` convention.

Examples:
- `base.g.node.class`
- `sh.actor.role`
- `market.quantity.unit`

## Schema Structure

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

## Required Fields

- `$schema`
  - SHALL reference JSON Schema draft 2020-12

- `$id`
  - SHALL equal the canonical schema URL
  - SHALL match the corresponding `schema_url` in `registry.yaml`

- `title`
  - SHALL equal the enum name

- `type`
  - SHALL be `"string"` or `"integer"`
  - SHALL be `"integer"` if and only if the corresponding enum registry
    entry has `value_type: "integer"`
  - SHALL be `"string"` if the corresponding enum registry entry omits
    `value_type`

- `description`
  - SHALL describe the semantic role of the enum

- `enum`
  - SHALL list all allowed values for this version

- `default`
  - SHALL be one of the declared enum values

## `x-gridworks` Metadata

Each enum schema SHALL include:

```
x-gridworks:
  owner: "<owner-id>"
  version: "<3-digit version>"
```

### Requirements

- `owner`
  - SHALL match the owner declared in `registry.yaml`

- `version`
  - SHALL be a three-digit numeric string
  - SHALL match the version encoded in `$id`

## Optional Metadata

```
x-gridworks:
  value_descriptions:
    "<EnumValue>": "<Description>"

x-gridworks:
  extended_description: >
    ...
```

### Rules

- `value_descriptions`
  - MAY appear only within `x-gridworks`
  - SHOULD include an entry for each enum value
  - SHOULD describe semantic meaning, not restate the name

- `extended_description`
  - MAY appear only within `x-gridworks`
  - MAY provide architectural or contextual explanation
  - MUST NOT introduce new normative constraints
  - MUST NOT change the meaning of any enum value

## Structured Enums

A **structured enum** is an ordinary enum (`literal` or `versioned`,
`string`-valued) that additionally declares, per value, a row of typed
**attributes** — a faithful, machine-readable decode of the value token (e.g.
the slot timing a market-product token encodes). Attributes are **vocabulary
metadata**, not serialized message fields: the on-the-wire value stays the bare
token, so Principle 2 (CamelCase serialized fields) and Principle 2a are
untouched. The decode is available at authoring and codegen time, carried by the
vocabulary word itself, and is the structural expression of Principle 4
(semantics that affect interpretation are declared in the schema, not left to
comments or code).

"Structured" is **orthogonal** to `enum_type`: a structured enum MAY be `literal`
or `versioned`. An enum is a structured enum **iff** it carries
`value_attribute_schema`.

```
x-gridworks:
  value_attribute_schema:
    "<attribute-name>": { type: string|integer|number|boolean }
  value_attributes:
    "<EnumValue>": { "<attribute-name>": <primitive> }
```

### Rules

- `value_attribute_schema`
  - MAY appear only within `x-gridworks`
  - declares the columns once: a map of `<attribute-name>` →
    `{ type: "string" | "integer" | "number" | "boolean" }`
  - attribute names use snake_case (they are not serialized fields, so the
    CamelCase rule does not bind them; snake_case matches their codegen surface)
  - every column is implicitly nullable (a value's row MAY set it `null`);
    `type` constrains the non-null values
  - the enum `type` SHALL be `"string"` (integer structured enums are not yet
    supported)

- `value_attributes`
  - MAY appear only within `x-gridworks`, and only when
    `value_attribute_schema` is also present
  - the rows: a map of `<EnumValue>` → `{ <attribute-name>: <primitive> }`
  - each row SHALL conform to `value_attribute_schema` (every declared column
    present; each value matching its declared `type`, or `null`)

### Structured-enum invariants

1. **Totality.** Every enum value SHALL have exactly one attribute row, and each
   row SHALL provide a value for *every* declared column. A structured enum is a
   *total* decode. **Exemption:** only the single value named in `default` MAY
   omit its row, decoding to a null attribute record. An enum with no `default`
   has no exempt value and SHALL be row-total. Enforced at authoring/registry
   validation (build-time), the same pass that checks `value_descriptions`.
2. **Primitive, dependency-free attributes.** Attribute values SHALL be JSON
   primitives (`string`, `integer`, `number`, `boolean`, `null`). An attribute
   value SHALL NOT be a `$ref` to any other Sema vocabulary, and SHALL NOT be a
   nested object or array. This keeps a structured enum a closure leaf: it
   introduces no new dependency edges. (A token like `"AvgkW"` is a bare string
   literal here, not a reference to `market.quantity.unit`; for v1 columns are
   free text.)
3. **Attribute immutability per value.** Once a value's attribute row is
   published, the existing **cells** of that row SHALL NOT change in any later
   version — the same stability rule enums apply to value *meaning*. A changed
   decode of an existing column means a new value, not a mutated cell.
4. **Additive attribute schema.** In a `versioned` structured enum a new version
   MAY **add** an attribute column (appended after existing columns; never
   inserted, removed, renamed, reordered, or retyped) and SHALL then populate it
   for *every* existing value, preserving totality. The back-populated cell is
   frozen by invariant 3 from the version it ships in. `literal` structured enums
   have a fixed attribute schema (version `000` only).

## Forbidden Extra Fields

Enum schema files SHALL NOT include any top-level fields other than:

- `$schema`
- `$id`
- `title`
- `type`
- `description`
- `enum`
- `default`
- `x-gridworks`

Within `x-gridworks`, enum schema files SHALL NOT include any fields
other than:

- `owner`
- `version`
- `value_descriptions`
- `extended_description`
- `value_attribute_schema`
- `value_attributes`

## Evolution Rules

Enum evolution is determined by `enum_type`.

- `literal`
  - SHALL have version `"000"`
  - SHALL define a fixed set of values
  - SHALL NOT add, remove, reorder, or reinterpret values
  - SHALL NOT change the default

- `versioned`
  - Each schema file defines a single version
  - New versions MAY append values to the end of the `enum` list
  - Values present in prior versions SHALL appear in the same relative
    order
  - SHALL NOT remove or reorder existing values
  - SHALL NOT change the semantic meaning of existing values
  - SHALL NOT change the default

## Description Evolution

In new versions of a `versioned` enum, the following MAY be updated:

- `description`
- `value_descriptions`
- `extended_description`

Such updates:

- MUST NOT change semantic meaning
- MUST NOT reinterpret prior behavior
- MUST NOT introduce new normative constraints

If semantic meaning changes, a new enum value MUST be introduced instead.

## Example: `base.g.node.class v000` (Enum)

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
      A physical transactive asset such as a heat pump, hot water heater,
      residential battery, electric vehicle, or any other end-use device
      located behind an atomic metered point.

    "LeafTransactiveNode": >
      The atomic metered unit of the grid. Represents the smallest
      indivisible metering boundary capable of participating in markets or
      entering Dispatch Contracts on behalf of a TerminalAsset. Every
      TerminalAsset is associated with exactly one LeafTransactiveNode.

    "ConnectivityNode": >
      A physical topological node in the electric power system where
      conductors join, split, or change configuration. Conceptually
      aligned with the ConnectivityNode in the IEC 61970/61968 CIM (Common
      Information Model), but simplified for distribution-level modeling
      and OPF applications.

    "MarketMaker": >
      A physical constraint point in the conductor topology that requires
      localized market coordination. Identified as a grid location (e.g.,
      feeder constraint, transformer limit) where a MarketMaker actor
      computes local prices for balancing and constraint compliance.
      See https://gridworks.readthedocs.io/en/latest/market-maker.html.

    "Logical": >
      A non-physical Grid Node whose identity carries no inherent
      conductor-topology or metering semantics. Used for purely logical or
      service-level nodes such as SCADA, forecasting services,
      market-maker actors, simulation nodes, or organizational
      microservices. Logical nodes may coordinate with or operate on
      physical nodes, but do not themselves represent physical grid
      structure.
```
