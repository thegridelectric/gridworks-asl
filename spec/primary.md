# Sema Specification — Primary

Version 1.0 · A Shared Vocabulary for Distributed Coordination
Originated by GridWorks Energy Consulting

This is the hub for the Sema specification. Sema is a versioned ontology
expressed as JSON Schema for validating serialized messages exchanged
between independent applications.

This document covers what Sema is, the core principles every reader needs
in active context, the cross-cutting overview, the glossary, and a map to
the sub-specs.

## What Sema governs

**Sema governs the structure and semantics of serialized JSON exchanged
between independent applications.** Validation applies to the concrete JSON
artifacts that cross system boundaries — not to local type hints, IDE
models, or in-memory representations.

Sema vocabulary is defined through versioned JSON Schema documents written
in YAML. Each schema serves as a contract defining structure, constraints,
identity, ownership, and evolution. These schemas collectively form a
shared ontology: a governed vocabulary describing how independent systems
represent and exchange meaning.

Schemas are:
- Machine-readable, human-readable, and language-neutral
- Versioned with controlled change
- Dependency-tracked
- Suitable for automated validation and code generation

Schemas are transport-agnostic. Sema does not mandate HTTP, MQTT,
WebSockets, or any specific runtime architecture. Systems may adopt Sema
incrementally — as a single format, a single type, or an entire vocabulary
tree.

For the purposes of immutability and version governance, a vocabulary
definition's lifecycle is its registry `status`: `draft` (not ready for
use), `staging` (in real use, still mutable in place, dev brokers only), or
`published` (immutable). Before publication, a schema MAY be revised in
place to correct mistakes or to better align the initial Sema contract with
demonstrated runtime behavior. After publication, historical versions are
immutable and any semantic or validation change SHALL be expressed through
a new version. Serving a definition at `https://schemas.electricity.works`
is a separate, later event that only published definitions are eligible
for; going live at the URL does not change status. See
[registry/structure.md](registry/structure.md) "Status Field".

## Core Principles

These principles apply to all Sema vocabulary definitions and all
serialized messages validated under Sema. They are the cross-cutting
invariants — every sub-spec assumes these.

**1. Vocabulary is Named.** Every vocabulary component has a globally
unique name using `left.right.dot` format. Names are not hierarchical
inheritance; they are stable semantic identifiers. Examples: formats like
`uuid4.str`, `utc.seconds`; enums like `base.g.node.class`, `gw1.unit`;
types like `bid`, `report`. These names are used for validation,
dependency tracking, and composition.

**2. Serialized Fields Use CamelCase.** All serialized JSON field names
MUST use CamelCase, recursively through nested structures.

```
✅ {"Bar": "bar", "TypeName": "foobar", "FooList": [{"Foo": "foo", "TypeName": "foo"}]}
❌ {"Bar": "bar", "TypeName": "foobar", "FooList": [{"foo": "fools", "TypeName": "foo"}]}
```

This ensures uniform structure across systems and prevents semantic drift
caused by naming inconsistencies. It also helps signal Sema.

**2a. Primitive Types Are Validated at the Serialized Boundary.** Sema
validation applies to the serialized JSON artifact as transmitted, not to
a permissively coerced in-memory approximation. If a schema says a value
is an `integer`, the serialized value MUST itself be an integer.
Implementations SHALL reject floats, strings, or other values that would
only satisfy the schema after coercion or truncation.

**3. Types Declare Their Identity.** Every type MUST include a `TypeName`
field whose value equals the registered vocabulary name. For versioned
types, a `Version` field is also required.

```
✅ {"Watts": 3723, "TypeName": "power.watts", "Version": "000"}
❌ {"Watts": 3723}
```

Type identity is explicit. Messages are self-describing and
machine-verifiable.

**4. Semantics at the Boundary Must Be Declared.** Sema is designed to
make semantic meaning explicit at the serialization boundary. If a
semantic fact affects how a value is validated, transformed, composed, or
interpreted across system boundaries, it SHALL be declared in the schema.

Meaning that influences interoperability SHALL NOT rely solely on field
names, code conventions, comments, or external documentation. Instead,
semantics that affect cross-system behavior must be structurally
represented in the serialized contract.

For example, if two values must be compatible for composition, that
compatibility must be declared in a way that can be validated mechanically.
If a new semantic distinction is introduced, it requires a new version.

This design enables mechanical validation, safe composition, AI-assisted
reasoning, and long-term interoperability without hidden assumptions. Sema
does not prescribe domain modeling style. It ensures that when semantics
matter for distributed coordination, they are visible and verifiable in
the serialized artifact itself.

**5. Vocabulary Scope and Adoption.** Registration in `registry.yaml`
establishes uniqueness and governance — not universal adoption. Publishing
a vocabulary word does not imply that all Sema participants must or are
expected to use it. Vocabulary words are namespace-scoped. Organizations
MAY and are encouraged to define their own vocabularies under distinct
namespaces (e.g., `gw.*`, `acme.*`, `utilityX.*`). Universal adoption is
determined by ecosystem coordination, not by registry presence.

## How this spec is organized

The spec is hub-and-spoke. Read this hub plus the spokes relevant to your
task; do not assume any spoke duplicates principles or invariants from
this hub.

- **[registry/](registry/)** — the lifecycle metadata that lives in
  `registry.yaml`. One file per kind.
  - [registry/structure.md](registry/structure.md) — top-level structure,
    metadata block, timestamp rules, status field, `replaced_by`,
    `owners.yaml`.
  - [registry/formats.md](registry/formats.md) — format entries.
  - [registry/enums.md](registry/enums.md) — literal and versioned enum
    entries.
  - [registry/types.md](registry/types.md) — type entries, versioning
    semantics, strategy evolution, new versions, immutability, dependency
    model.

- **[authoring/](authoring/)** — the rules for writing the schema files
  themselves (the YAML in `definitions/`). One file per kind, with type
  authoring split across three files because of size.
  - [authoring/formats.md](authoring/formats.md) — writing format schema
    files (+ `utc.milliseconds` example).
  - [authoring/enums.md](authoring/enums.md) — writing enum schema files
    (+ `base.g.node.class` example).
  - [authoring/types.md](authoring/types.md) — writing type schema files:
    structure, identity, properties, primitive constraint rule,
    composition, const, inline objects, references,
    `additionalProperties`.
  - [authoring/type-semantics.md](authoring/type-semantics.md) —
    `x-gridworks` metadata, projections, axioms, `extended_description`,
    SDK extensions, **upgrade discipline**.
  - [authoring/type-examples.md](authoring/type-examples.md) — `bid v000`
    and `report v002` worked examples.

- **[governance.md](governance.md)** — ownership responsibilities,
  vocabulary naming discipline, registration process, change process,
  conflict resolution, reserved namespaces. The canonical home for "how
  vocabulary gets in and how it changes."

- **[snapshot.md](snapshot.md)** — the tooling contract for producing a
  **restricted runtime snapshot** for a consumer: determinism (zero-diff
  regen), atomic build, the generated `samples/`, and the round-trip gate
  (including the context-dependent-upgrade exemption). Language-neutral
  guarantees; the reference implementation is the Python SDK under
  `src/sema/tools/`.

## Glossary

| Term | Meaning |
|---|---|
| **format** | Immutable, unversioned vocabulary word that refines a JSON primitive (`string`, `integer`, `number`, `boolean`) with validation constraints. Examples: `uuid4.str`, `utc.seconds`. Cannot reference other Sema vocabulary. |
| **enum** | Vocabulary word defining a closed set of named values. `literal` enums are fixed; `versioned` enums are additive over time. Value type is `string` (default) or `integer`. |
| **type** | Structured, versioned semantic contract. Types may reference formats, enums, and other versioned types. Types are what get serialized between applications. |
| **versioned** type | Type with `versioning_strategy: "string"` or `"literal"`. Versions are three-digit numeric strings (`"000"`, `"001"`, …) in strict order. |
| **versionless** type | Type with `versioning_strategy: "none"`. No `versions` block; single `schema_url`. |
| **versioning strategy** | `none` → `string` → `literal`. Monotonic; a type may only adopt a stricter strategy, never relax. |
| **structural dependency** | A vocabulary word referenced via `$ref` in the schema. |
| **axiom dependency** | A vocabulary word required to implement one or more axioms for a type version, but not referenced via `$ref`. |
| **projection** | Declared deterministic mapping between two enum-valued properties of a type, with an exhaustive table covering every source value. |
| **axiom** | A semantic invariant that cannot be expressed via structural JSON Schema constraints. Numbered per type version. |
| **draft** / **staging** / **published** | Lifecycle status (`status`, required on every registry entry). Drafts are mutable and not usable; excluded from `latest_version`. Staging vocabulary is in real use but still mutable — dev brokers only. Published vocabulary is immutable. |
| **replaced_by** | Advisory hint on a vocabulary word pointing at successor words. Does not affect validation, lifecycle, or dependency closure. |
| **owner** | Identifier from `owners.yaml`. Every vocabulary word has exactly one owner. |

## Source precedence

When sources conflict about a type version's behavior, resolve in this
order:

1. **The schema file** for the relevant version — runtime correctness.
2. **`registry.yaml`** — lifecycle and discovery metadata.
3. **This specification** — the structural and evolutionary rules.

Schema validation behavior always governs runtime correctness. Registry
metadata governs lifecycle and discovery. The specification governs
structure and evolution; when implementations conflict with the
specification, the specification governs and implementations SHALL be
corrected.
