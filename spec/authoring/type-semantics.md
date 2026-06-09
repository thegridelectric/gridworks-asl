# Authoring — Type Semantics (Metadata, Projections, Axioms, Upgrades)

This sub-spec covers the **semantic** concerns of a type schema:
`x-gridworks` metadata, projections, axioms, `extended_description`, SDK
extensions, and upgrade discipline.

Structural concerns (top-level layout, properties, references,
`additionalProperties`) are in [types.md](types.md). Worked examples are
in [type-examples.md](type-examples.md).

Read [../primary.md](../primary.md) for core principles.

## `x-gridworks` Metadata

All schemas MUST include:

```
x-gridworks:
  owner: "<owner-id>"
```

Optional fields include `axioms` and `extended_description`.

Within `x-gridworks`, fields SHALL appear in the following order when
present: `owner`, `supersedes` (if applicable), `projection` (if any),
`axioms` (if any), `extended_description` (if any).

## Projections

A projection is a structural declaration of a deterministic mapping
between two enum-valued properties of a type. When present, it SHALL
appear under `x-gridworks.projection`.

A projection declares:
- A source property (`from`) whose value is constrained to an enum
- A target property (`to`) whose value is constrained to an enum
- An exhaustive `table` mapping every value of the source enum to a
  value of the target enum

A type SHALL declare at most one projection.

### Structure

```
x-gridworks:
  projection:
    from: <PropertyName>
    to: <PropertyName>
    table:
      <SourceEnumValue>: <TargetEnumValue>
      ...
```

### Field Requirements

- `from`
  - SHALL be the name of a property declared in `properties`
  - The named property SHALL reference a Sema enum via `$ref`

- `to`
  - SHALL be the name of a property declared in `properties`
  - The named property SHALL reference a Sema enum via `$ref`
  - SHALL NOT equal `from`

- `table`
  - SHALL contain one entry for every value of the source enum (totality)
  - Each value SHALL be a declared value of the target enum
  - Keys SHALL be unique

The source and target enums are identified through the `$ref` of the
named properties. They appear in `direct_dependencies.structural` by
virtue of those property references and SHALL NOT be redeclared as axiom
dependencies.

### Semantics

A projection establishes a structural invariant: for any valid instance
of the type, the value of the target property SHALL equal the value
associated with the value of the source property in `table`.

A type that declares a projection SHALL also declare an axiom that
references the projection table. The axiom SHALL NOT restate the table
inline. This ensures the mapping has a single authoritative
representation.

### Evolution

When the source enum adds a value, totality requires the projection
table to be extended. Such an extension SHALL be expressed through a new
version of the projection type. Entries present in prior versions SHALL
NOT be modified or removed in subsequent versions.

### SDK Implementations

SDK implementations of a type that declares a projection SHOULD provide
an accessor that returns the target value for a given source value,
derived from `table`. Such accessors are non-serialized extensions as
defined in *SDK Implementations and Non-Serialized Extensions* and SHALL
NOT alter the serialized contract.

## Axioms

Axioms describe semantic invariants that cannot be expressed through
structural JSON Schema constraints.

Each axiom SHALL:

- Be numbered using positive integers starting at 1 (1, 2, 3, …).
- Appear in ascending numeric order.
- Use normative language (SHALL, MUST).
- Not restate structural constraints already enforced by the schema.
- Be specific to a particular `TypeName` + `Version`.

Axiom numbering is scoped to a specific type version. When a new version
of a type is created, axioms MAY be renumbered starting at 1.

In YAML, axioms SHALL be represented under `x-gridworks.axioms` as an
ordered list. Each axiom entry SHALL include:

- `number` — integer number
- `name` — short identifier
- `statement` — normative statement

Example:

```
x-gridworks:
  axioms:
    - number: 1
      name: "NonEmptyLists"
      statement: "ValueList and ScadaReadTimeUnixMsList SHALL be non-empty."
    - number: 2
      name: "ListLengthConsistency"
      statement: "len(ValueList) SHALL equal len(ScadaReadTimeUnixMsList)."
```

### Axiom Clause Labels and Counterexamples

An axiom statement may contain one or more independently testable
validation obligations. If an axiom requires multiple distinct negative
examples, those obligations SHALL be enumerated within the statement
using lowercase labels `a.`, `b.`, `c.`, and so on.

Clause labels are test and code-generation aids. They do not create
separate axioms, alter axiom numbering, or change version semantics. The
axiom remains identified by its `number` and `name`.

Clause labels SHALL be used only when each labeled clause corresponds to
a distinct counterexample obligation. Explanatory text SHALL NOT be
labeled. If multiple checks can be naturally expressed as one validation
condition, the axiom SHOULD remain a single unlabeled clause.

For runtime validation tests, counterexample fixtures SHOULD follow this
naming convention:

```text
axiom_<number>.json
```

for a single-clause axiom, and:

```text
axiom_<number>_<label>.json
```

for a multi-clause axiom, where `<label>` is the lowercase clause label.

Example:

```yaml
x-gridworks:
  axioms:
    - number: 1
      name: "ClassConsistency"
      statement: >
        a. If BaseClass is not Logical, GNodeClass SHALL equal the string value of BaseClass.
        b. If BaseClass is Logical, GNodeClass SHALL NOT equal any value of base.g.node.class other than Logical.
```

The corresponding negative examples SHOULD be named:

```text
axiom_1_a.json
axiom_1_b.json
```

SDK implementations SHOULD provide one validation function per axiom. In
the Python SDK, validator functions SHALL be named:

```
check_axiom_<n>
```

where `<n>` is the axiom number.

## `extended_description`

`extended_description` provides architectural context, rationale, and
system-level explanation. It SHALL NOT duplicate `description`.

## SDK Implementations and Non-Serialized Extensions

Sema defines the structure and semantics of serialized JSON exchanged
between independent applications. SDK implementations MAY provide
additional computed properties, helper methods, validation utilities, or
convenience accessors that are not present in the serialized schema.

Such extensions:

- SHALL NOT alter or extend the serialized contract.
- SHALL NOT introduce additional serialized fields unless explicitly
  defined in the schema.
- SHALL NOT modify validation behavior defined by the schema and axioms.

These implementation-level conveniences are language-specific and are not
considered part of the Sema vocabulary.

## Upgrade Discipline

When a versioned type publishes a new version, runtime implementations
MUST provide an upgrade path that converts a valid instance of the prior
version into a valid instance of the new version. This section governs
the discipline that upgrade implementations SHALL follow, independent of
implementation language.

### Upgrade Invariants

A version upgrade implementation MUST be:

- **Minimal** — only fields whose values or semantics change between
  versions SHALL be modified.
- **Schema-preserving** — the output instance SHALL validate against the
  new version's schema with no manual reconstruction of unchanged
  fields.
- **Forward-compatible** — the upgrade SHALL produce an instance whose
  semantics are consistent with the new version's contract; it SHALL NOT
  embed legacy assumptions that the new version retired.

Upgrade implementations SHALL NOT manually reconstruct objects
field-by-field. Field-by-field reconstruction risks omitting fields
present in the prior version but absent from the implementer's
attention, and silently dropping data.

### Canonical Upgrade Pattern

For any versioned type, the canonical upgrade pattern is:

1. Serialize the prior-version instance to its structural representation
   (e.g., a dict).
2. Modify only the fields whose value or representation changes in the
   new version.
3. Validate the modified structure against the new version's schema to
   produce the new-version instance.

In the Python SDK this maps directly to:

- `model_dump()` — produces the structural dict.
- mutate the dict to apply the version delta.
- `model_validate()` on the new-version class — produces the
  new-version instance.

### Nested Upgrades

Nested Sema types MUST be upgraded recursively. If a type contains a
field whose value is another Sema type (or a list of them), and that
nested type's version has changed between the outer type's old and new
versions, each nested instance SHALL be upgraded via its own upgrade
implementation before the outer-type upgrade completes.

In the Python SDK, this is conventionally exposed as a `.upgrade()`
method on each versioned type class.

### Required-Property Additions

When a new version of a type adds a required property that did not exist
in the prior version, the upgrade implementation MUST define how the
value is assigned. Optional defaults declared in the schema SHALL NOT be
relied upon for this purpose (see [types.md — Property
Definitions](types.md#property-definitions)). The upgrade implementation
is the canonical place for the assignment rule.

### Context-Dependent Upgrades

Some `old → new` upgrades cannot be performed on a standalone instance
because the transformation needs information the isolated message does not
carry — for example, a new version that replaces inline node/channel stubs
with full vocabulary objects requiring handles or ids that only the source
**layout** holds, or a field that can only be derived from the originating
**request**. Such an upgrade SHALL NOT fabricate or guess the missing
values. It MUST refuse, and it SHALL signal the refusal with a typed,
machine-detectable error rather than a generic one.

In the Python SDK this is the `UpgradeRequiresContext` exception (a
`SemaError`/`ValueError` subclass on the runtime base), raised via
`SemaType.upgrade_requires_context(<reason>)`. Tooling that exercises the
upgrade chain (the snapshot round-trip gate) treats `UpgradeRequiresContext`
as an **expected outcome**, not a failure: a version with a context-dependent
upgrade is still required to carry an `examples:` entry and still MUST
round-trip at its **own** version (decode → re-encode), but is exempt from
the `decode-old → upgrade() → decode-current` leg. A context-dependent
upgrade is a property of the version transition, not a license to skip the
example — the own-version round-trip is what proves the (possibly restricted)
runtime can still decode that version's wire form.
