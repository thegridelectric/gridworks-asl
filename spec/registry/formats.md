# Registry — Format Entries

This sub-spec covers `registry.yaml` entries for **formats**. For writing
the format schema files themselves, see
[../authoring/formats.md](../authoring/formats.md). For cross-cutting
registry shape, see [structure.md](structure.md).

Read [../primary.md](../primary.md) for core principles.

## Format Entries

Formats are immutable and unversioned. Each format entry MUST include:

```
<format-name>:
  owner: <owner-id>
  schema_url: "https://schemas.electricity.works/formats/<format-name>"
  created: "<RFC 3339 timestamp>"
  description: "<concise structural description>"
```

For all vocabulary entries (formats, enums, and types), `schema_url`
SHALL equal the `$id` declared in the referenced schema file.

Formats SHALL NOT include any version-related information.
