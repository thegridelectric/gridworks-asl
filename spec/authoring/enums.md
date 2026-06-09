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
