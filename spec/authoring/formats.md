# Authoring — Format Schema Files

This sub-spec covers writing format schema files (the YAML in
`definitions/formats/`). For the `registry.yaml` entry shape, see
[../registry/formats.md](../registry/formats.md).

Read [../primary.md](../primary.md) for core principles.

## Purpose

Formats define reusable validation constraints for primitive values in
Sema. Formats are immutable vocabulary words that refine JSON primitive
types (e.g., `string`, `integer`) with additional structural or semantic
constraints.

Formats SHALL NOT reference other Sema vocabulary. This binds a format's
**validation behaviour**, not only its schema: a format's validator — and the
code generated from it — SHALL NOT depend on any other Sema vocabulary (e.g. a
pattern validator MUST NOT consult an enum's members). A format is a
dependency-free leaf; if validation genuinely needs another word, the construct
belongs in a type or an axiom, not a format.

## Naming

Format names SHALL use the `left.right.dot` convention.

Examples:
- `left.right.dot`
- `uuid4.str`
- `utc.seconds`

## Schema Structure

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

## Required Top-Level Fields

- `$schema` — MUST reference JSON Schema draft 2020-12.
- `$id` — MUST be the canonical public schema URL.
- `title` — MUST match the registered format name.
- `description` — MUST describe structural meaning.
- `type` — MUST be a JSON primitive (`string`, `integer`, `number`, or
  `boolean`).
- `x-gridworks.owner` — MUST identify the owning organization.

## Validation Constraints

Formats MAY use JSON Schema validation keywords appropriate to their
primitive type, including:

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

When declaring regular expression patterns in YAML schema files, the
pattern value SHALL be quoted as a string. This prevents YAML parsing
ambiguities and ensures consistent interpretation of escape sequences.
Double-quoted strings SHOULD be used, with backslashes escaped
appropriately (e.g., `"\\."` for a literal dot).

## Immutability

Formats are immutable once registered.

The validation pattern, constraints, and semantics of a format SHALL NOT
change after publication.

Formats do not have versions.

## Examples and Counterexamples

Format schemas SHOULD include:

- `examples` — Valid representative values
- `counterexamples` — Explicit invalid values with short inline
  explanations

Examples and counterexamples improve mechanical validation testing and
IDE support.

## Example: `utc.milliseconds` (Format)

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
