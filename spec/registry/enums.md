# Registry — Enum Entries

This sub-spec covers `registry.yaml` entries for **enums**. For writing
the enum schema files themselves, see
[../authoring/enums.md](../authoring/enums.md). For cross-cutting registry
shape, see [structure.md](structure.md).

Read [../primary.md](../primary.md) for core principles.

## Enum Entries

Enums define closed sets of named values.

Enums MAY be either:

- `literal` — fixed and non-evolving
- `versioned` — additive over time

The `enum_type` field determines how the enum evolves.

For enums, the registry SHALL record top-level `enum_type`. For enums, the
registry MAY record top-level `value_type`. If `value_type` is present, it
SHALL be `"integer"` and the corresponding enum schema file SHALL have
`type: integer`. If `value_type` is omitted from an enum registry entry,
it SHALL be interpreted as `"string"` and the corresponding enum schema
file SHALL have `type: string`. The enum schema file remains
authoritative; the registry copy exists for compact tooling and
validation.

---

## Literal Enum Structure

For `literal` enums:

```
<enum-name>:
  owner: <owner-id>
  enum_type: "literal"
  description: "<concise semantic description>"
  value_type: "integer"   # optional; omit for string-valued enums

  schema_url: "https://schemas.electricity.works/enums/<enum-name>/000"
  created: "<RFC 3339 timestamp>"
```

### Literal Enum Field Requirements

- `versions`
  - SHALL NOT be present

- `latest_version`
  - SHALL NOT be present

- `schema_url`
  - SHALL uniquely identify the enum schema
  - SHALL include version `"000"`

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC

- `status`
  - SHALL appear at the word level (see [structure.md](structure.md)
    "Status Field")

- `value_type`
  - MAY be present
  - if present, SHALL equal `"integer"`
  - if omitted, the enum SHALL be treated as string-valued

- Literal enums:
  - SHALL define a fixed set of values
  - SHALL NOT add or remove values

---

## Versioned Enum Structure

For `versioned` enums:

```
<enum-name>:
  latest_version: "<version>"
  owner: <owner-id>
  enum_type: "versioned"
  description: "<concise semantic description>"
  value_type: "integer"   # optional; omit for string-valued enums

  versions:
    "<version>":
      schema_url: "https://schemas.electricity.works/enums/<enum-name>/<version>"
      created: "<RFC 3339 timestamp>"
      added_values: "<list of values added in this version>"
    [..]  # earlier versions
```

### Versioned Enum Field Requirements

- `latest_version`
  - SHALL equal the highest non-draft (staging or published) version
    listed under `versions`

- `versions`
  - SHALL contain an entry for each published or staging version
  - Each version entry SHALL carry a required `status` (see
    [structure.md](structure.md) "Status Field")
  - SHALL be keyed by three-digit numeric strings
  - SHALL be listed in decreasing order by version

- `created`
  - SHALL be an RFC 3339 timestamp with seconds precision in UTC

- `added_values`
  - SHALL be present for all versions except the initial version in the
    registry
  - SHALL be a list of enum values added in that version

- `value_type`
  - MAY be present
  - if present, SHALL equal `"integer"`
  - if omitted, the enum SHALL be treated as string-valued
