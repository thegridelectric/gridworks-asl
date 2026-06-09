# Authoring — Type Schema Files (Structure & Properties)

This sub-spec covers the structural rules for writing type schema files
(the YAML in `definitions/types/`): top-level layout, identity fields,
property definitions, composition rules, references, and
`additionalProperties`.

Semantic concerns (axioms, projections, `extended_description`, SDK
extensions, upgrade discipline) are in
[type-semantics.md](type-semantics.md). Worked examples are in
[type-examples.md](type-examples.md).

For the `registry.yaml` entry shape and versioning semantics, see
[../registry/types.md](../registry/types.md). Read
[../primary.md](../primary.md) for core principles.

## Purpose

Types define structured, versioned semantic contracts in Sema.

Types may reference:

- Formats
- Enums
- Other versioned Sema types

Types are what get serialized/deserialized and sent between applications.
They are the primary building block of Sema.

## Identity Fields

All versioned types SHALL explicitly declare both:

- `TypeName`
- `Version` (if `versioning_strategy` is not `none`)

### TypeName

- MUST be present in `properties`
- MUST be declared using `const`
- MUST match the vocabulary name registered in `registry.yaml`

Example:

```
TypeName:
  const: "bid"
```

### Version

MUST follow the rules defined by `versioning_strategy`. See
[../registry/types.md](../registry/types.md).

## Version Strategy Semantics

Versioned types (`string` and `literal`) SHALL:

- Enumerate all versions explicitly in the registry
- Maintain strict version ordering
- Provide upgrade paths between versions

For upgrade discipline rules, see
[type-semantics.md#upgrade-discipline](type-semantics.md#upgrade-discipline).

## Required Top-Level Order

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
examples:        # Optional
x-gridworks:
```

## Schema Header Requirements

- `$schema` MUST reference JSON Schema draft 2020-12
- `$id` MUST be the canonical public schema URL
- `title` MUST match the vocabulary name registered in `registry.yaml`
- `description` MUST describe structural meaning

## Property Definitions

Each property SHALL include:

- `$ref` or `type`

and MAY include:

- `description`

Property descriptions are **strongly recommended** but not required. If
provided, descriptions SHOULD be complete sentences, describe semantic
meaning, and avoid implementation details.

Over time, high-value types SHOULD include complete property descriptions.

Optional properties SHALL NOT declare `default`. If a property needs a
default value, it SHALL be listed in `required`; otherwise the default
SHALL be removed and absence SHALL remain absence.

Sema does not use JSON Schema `default` as a semantic mechanism. Default
values for type properties MUST NOT be relied upon for validation or
interpretation and are instead applied explicitly by runtime
implementations, such as during version upgrade or decoding. When
introducing new required properties in a type version, the upgrade path
MUST define how values are assigned. Optional properties MUST NOT encode
implicit default behavior. Enum defaults remain the sole schema-level
default mechanism and MUST be stable across versions.

## Primitive Constraint Rule

Sema schemas SHALL NOT express primitive value constraints directly using
JSON Schema keywords such as `minimum`, `maximum`, `exclusiveMinimum`,
`exclusiveMaximum`, `pattern`, `minLength`, `maxLength`, or similar
constraint-bearing constructs. All such constraints MUST be represented
through named Sema formats, which serve as the canonical, reusable, and
version-stable carriers of primitive semantics.

JSON Schema within Sema type and enum schemas is restricted to structural
description and reference (`type`, `$ref`, `required`,
`additionalProperties`, and similar structural keywords) and MUST NOT be
used to introduce new semantic meaning at the field level. If a
constraint on a primitive value is required, it MUST be defined as a
format and referenced via `$ref`. This ensures that all primitive
semantics are explicit, reusable, and consistently enforced across
languages and implementations.

## Composition Rule

Type schemas MAY use `oneOf` only to express a closed union of registered
Sema vocabulary references. Each `oneOf` branch SHALL be an object
containing exactly one `$ref`, and that `$ref` SHALL reference either
`https://schemas.electricity.works/types/...` or
`https://schemas.electricity.works/enums/...`.

A `oneOf` MAY include multiple versions of the same versioned type
(e.g., `spaceheat.node.gt/300` and `spaceheat.node.gt/301`) to accept
instances from a bounded set of versions during version-transition
windows.

Type schemas SHALL NOT use `oneOf` with inline schemas, primitive
schemas, `const`, `enum`, formats, or constraint-bearing JSON Schema
constructs. Type schemas SHALL NOT define inline enums with the JSON
Schema `enum` keyword; such values SHALL be promoted to a named Sema enum
and referenced with `$ref`.

## Const Usage Rule

The JSON Schema keyword `const` SHALL be used only to declare fixed
identity values within Sema types.

Specifically, `const` is permitted only for:

- `TypeName`
- `Version`
- Fields that explicitly encode the identity of a Sema vocabulary element
  (e.g., `<Relation>TypeName` and `<Relation>Version` pairs that refer to
  another Sema type)

`const` MUST NOT be used to express constraints on ordinary data fields,
including numeric, boolean, or string values (e.g., `NumPhases = 3`,
`Enabled = true`). Such constraints MUST be represented using Sema
formats, enums, or types, or enforced through runtime logic where
appropriate.

If a value is invariant across all instances of a type, it SHOULD NOT be
modeled as a data field. Instead, it SHOULD either be omitted or encoded
as part of the type's identity.

## Inline Object Properties

Type schemas MAY include inline object definitions, but only as
semantically inert structural groupings.

An **inline object** is any schema node below the top-level named type
schema that:

- declares `type: object`
- declares `properties`
- is not a `$ref` to a registered Sema type

Inline objects exist to group fields locally within a containing type.
They do not define reusable vocabulary, semantic subtypes, or
independently meaningful boundary contracts. If a nested object carries
meaning that affects validation, composition, interoperability, axioms,
or code generation beyond its containing field structure, it SHALL be
promoted to a named Sema type and referenced with `$ref`.

Inline objects SHALL NOT contain semantic JSON Schema constructs,
including:

- `const`
- `enum`
- `oneOf`
- `anyOf`
- `allOf`

Inline object properties SHALL NOT reference Sema types. A `$ref` from
within an inline object MAY reference formats or enums when needed for
primitive or enumerated field validation, but SHALL NOT reference
`https://schemas.electricity.works/types/...`.

Inline objects SHALL NOT be referenced by axioms. Axioms for the
containing type SHALL NOT normatively refer to fields defined only inside
an inline object. If an invariant needs to name or constrain nested
fields, the nested object SHALL be promoted to a named Sema type and the
axiom SHALL be attached to that named type or to the containing type
through the referenced type boundary.

Inline object descriptions, and descriptions of fields within inline
objects, SHALL remain structural and non-normative. They SHALL NOT
include normative or semantic constraint language such as `SHALL`,
`MUST`, `only`, or `exactly`.

Inline objects MAY use ordinary structural JSON Schema keywords needed to
define local shape, such as:

- `properties`
- `required`
- `additionalProperties`
- primitive `type`

These permissions do not allow inline objects to carry semantic
constraints. When the distinction is ambiguous, schema authors SHALL
promote the object to a named Sema type.

## Open Containers

A schema node of the form `type: object` with no `properties:` and no
`additionalProperties:` is an **open container** — a placeholder for
content whose structural shape is not declared at this layer.
Open containers MAY appear inside type schemas
(e.g., `derived.channel.gt`'s `Parameters` field).

Axioms MAY reference an open container's contents **only when the
axiom encodes a discriminated or conditional structure** — that is,
when the required shape of the container depends on the value of a
sibling field of the containing type. The canonical example is
`derived.channel.gt`'s axioms 3 and 4: `Parameters`' shape depends on
the value of the sibling `Strategy` enum field.

Axioms SHALL NOT use an open container to encode **unconditional**
structure. If a `type: object` field's shape is fixed and known at
design time, the schema SHALL express that shape directly — via
`properties:`, by promoting to a named Sema type, or (when keyed-dict
semantics are required) via the Typed Map pattern defined below.

Rationale: see core principle 4 ("Semantics at the Boundary Must Be
Declared"). Unconditional structure belongs in the schema where it can
be mechanically validated and code-generated; conditional structure
that Sema's restricted composition cannot express is the legitimate
axiom case.

## Typed Maps

A **typed map** is a `type: object` node that declares both:

- `propertyNames: { $ref: <canonical Sema format URL> }` — fixing the
  shape of the dictionary keys
- `additionalProperties: { $ref: <canonical Sema type URL> }` — fixing
  the value type

Typed maps MAY appear inside type schemas. The `propertyNames`
constraint is the structural signal that the dictionary keys carry
semantic content (typically an index, identifier, or categorical
label) distinct from any field on the value type.

A `type: object` with `additionalProperties: $ref → types/...` but
**no `propertyNames:`** SHALL NOT appear. The keys would be arbitrary
handles — typically redundant with a field already on the value type.
Such a collection SHALL instead be expressed as a typed array
(`type: array, items: $ref → types/...`) or promoted to a named Sema
type.

### Blessed key formats

A typed map's `propertyNames.$ref` SHALL reference one of the
following key formats:

- `non.empty.string` — any non-empty string key (free-form
  identifiers).
- `positive.int.as.str` — string form of a positive integer
  (`"1"`, `"2"`, ...). Used when keys are tank indices, sequence
  positions, or other integer-like labels.

Adding a new key format SHALL be justified by at least one concrete
schema consumer. The construct's mental model (keys are either
free-form strings or integer-shaped strings) is load-bearing and the
spec SHALL be conservative about widening it.

### Example

```yaml
Tank:
  type: object
  propertyNames:
    $ref: "https://schemas.electricity.works/formats/positive.int.as.str"
  additionalProperties:
    $ref: "https://schemas.electricity.works/types/gw1.tank.temp.calibration/000"
```

### Dependencies

The value type referenced via `additionalProperties.$ref` appears in
`direct_dependencies.structural` by virtue of the `$ref`. The key
format referenced via `propertyNames.$ref` SHALL likewise appear in
`direct_dependencies.structural`.

### Axioms on typed maps

The Open Containers rule above applies. A typed map's `propertyNames`
+ `additionalProperties` already enforce key shape and value type
structurally; axioms on a typed map's contents are reserved for
**discriminator / conditional** cases (the same exception that
justifies derived.channel.gt's axioms 3 and 4). Unconditional axioms
about a typed map's contents SHALL NOT be added — express the
constraint in `propertyNames` / `additionalProperties` or refactor.

## Referencing Other Vocabulary

Every `$ref` value in a type or enum schema SHALL be a canonical Sema
schema URL of one of the following shapes:

- `https://schemas.electricity.works/formats/<format-name>`
- `https://schemas.electricity.works/enums/<enum-name>/<3-digit-version>`
- `https://schemas.electricity.works/types/<type-name>` (versionless)
- `https://schemas.electricity.works/types/<type-name>/<3-digit-version>` (versioned)

(Draft schemas use the parallel `…/draft/{formats,enums,types}/…`
prefix per the draft-publication rules.) A `$ref` value SHALL NOT be a
bare JSON Schema primitive name (`"string"`, `"integer"`, etc.), a
relative path, a fragment, or any other non-canonical string.

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

## Required Property Declarations

All required declarations MUST be explicitly listed under `required`.

## `additionalProperties` Rule

The preferred default for Sema types is:

```
additionalProperties: false
```

This prevents unintended schema drift and enforces explicit semantic
contracts.

However, types under active schema evolution, or types that serve as
flexible aggregation or embedding layers, MAY declare:

```
additionalProperties: true
```

Over time, as schemas stabilize, types SHOULD transition toward:

```
additionalProperties: false
```

## Examples

Types MAY include an `examples` field. It is **optional for the latest version
of a type and for versionless types**, but **a superseded type version MUST
carry at least one `examples:` entry** (see *Superseded versions* below).

If present:

- Examples SHALL be serialized JSON documents, not YAML object
  representations
- Examples SHALL be structurally valid according to the schema
- Examples SHOULD represent the smallest semantically valid instance of
  the type (minimal canonical example)
- Examples MAY include a realistic instance in addition to the minimal
  example
- Examples MUST NOT contradict any declared axioms

Examples serve as:

- Developer guidance
- IDE assistance
- Validation fixtures
- Contract clarity for integrators

Example structure:

```
examples:
  - |
    {
      "TypeName": "example.type",
      "Version": "000",
      ...
    }
```

Examples are optional but strongly recommended for public-facing types
and core system messages.

### Superseded versions

A type version that has a successor (a numerically higher version exists for the
same type) is **superseded** and MUST carry at least one `examples:` entry. The
mandate binds only once a version has a successor — the latest version stays
optional (above).

Rationale: superseded versions exist precisely to be **upgraded**, and the
`decode-old → upgrade() → decode-current` path is where snapshot/runtime bugs
concentrate (a restricted snapshot whose vocabulary no longer matches the older
data it must carry). The example is the fixture the snapshot round-trip
exercises against that version, so a superseded version without one is silently
untested. Adding an example to an already-published version is permitted — it is
non-normative and alters no validation behavior (see
[../registry/types.md](../registry/types.md) "Permitted Changes (All Types)").
