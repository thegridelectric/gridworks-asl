# Registry — Structure

This sub-spec covers the cross-cutting shape of `registry.yaml`: top-level
layout, metadata block, timestamp rules, status field, `replaced_by`, and
the companion `owners.yaml` file. For per-kind entry rules see
[formats.md](formats.md), [enums.md](enums.md), and [types.md](types.md).

Read [../primary.md](../primary.md) for core principles.

## The Registry's Role

The `registry.yaml` file is the authoritative index of all Sema vocabulary
components. It defines:

- What vocabulary words exist
- Their ownership
- Their versioning strategy
- Their current latest version
- Their dependency relationships

The registry is the canonical source of vocabulary identity and lifecycle
state. Vocabulary components fall into three categories: **formats**,
**enums**, and **types**.

## Top-Level Structure

1. The registry SHALL contain the following top-level sections in this
   order:

   ```
   metadata:
   formats:
   enums:
   types:
   ```

2. Entries within each section SHALL be listed in alphabetical order.

3. For versioned types, versions SHALL be listed in reverse chronological
   order (newest first).

## Metadata Block

```
metadata:
  registry_version: "1.0"
  last_updated: "2025-06-24T10:30:00Z"
  maintainer: "gridworks-energy"
```

- `registry_version` — Version of the registry structure itself.
- `last_updated` — RFC 3339 timestamp.
- `maintainer` — Responsible organization.

## Timestamp Rules

All registry timestamps SHALL:

- Conform to RFC 3339
- Include full date and time components
- Include seconds precision (HH:MM:SS)
- Use UTC with the `Z` suffix
- NOT include fractional seconds
- Represent the publication time of the vocabulary entry in the registry

Example: `"2026-02-22T16:43:00Z"`.

## Status Field

Registry entries MAY include a `status` field indicating publication
lifecycle state.

Allowed values:
- `"draft"` — vocabulary definition is mutable and not yet published
- `"published"` — vocabulary definition is immutable per this
  specification

For versionless vocabulary words (formats and versionless types), `status`
MAY appear on the word entry. If omitted, it SHALL be interpreted as
`"published"`.

For versioned enums and versioned types, `status` applies to individual
version entries under `versions`. If omitted from a version entry, it
SHALL be interpreted as `"published"`.

A versioned enum or type MAY have both published and draft versions at
the same time. In that case:

- `latest_version` SHALL identify the latest published version
- Draft versions SHALL NOT be selected by `latest_version`
- Draft versions MAY be numerically greater than `latest_version`
- Tooling MAY expose draft versions only when explicitly requested

Draft definitions MAY appear in the working registry and in local schema
files. Draft definitions SHALL NOT be published to
`https://schemas.electricity.works` and SHALL be excluded from public
schema indexes, public schema pages, and default public schema serving.

For draft definitions, `created` records the time the draft entry was
first added to the working registry. When a draft definition is promoted
to published, `created` SHALL be updated to the publication timestamp.
From that point forward, `created` is governed by the immutability rules
for published definitions.

If a draft schema file appears under `definitions/`, it SHALL remain
parseable YAML and SHALL use the normal Sema schema file layout. Draft
status relaxes immutability and may relax completeness checks defined by
tooling, but it does not permit malformed schema files.

## `replaced_by` Field

Registry word entries MAY include a `replaced_by` field as advisory
metadata.

`replaced_by`:

- SHALL appear only on a vocabulary word entry, not on a version entry
- SHALL reference one or more vocabulary word names
- SHALL NOT include version suffixes
- SHALL NOT include URL prefixes or file paths
- SHALL reference existing words in the registry

Example:

```yaml
old.word:
  owner: gridworks-energy
  replaced_by:
    - new.word
```

`replaced_by` is a hint for humans, documentation, migration tooling, and
AI-assisted review. It does not create a lifecycle state.

Specifically, `replaced_by`:

- does not invalidate the current word or any version of it
- does not affect schema validation
- does not affect dependency closure
- does not affect version ordering
- does not affect `latest_version`
- does not imply semantic equivalence
- does not create an automatic upgrade or migration path
- does not alter immutability requirements for published definitions

## `owners.yaml` — Vocabulary Ownership Registry

The `owners.yaml` file defines the authoritative registry of vocabulary
owners. Every vocabulary word in `registry.yaml` MUST reference an owner
declared in `owners.yaml`.

Owner identifiers:
- SHALL be lowercase kebab-case strings
- SHALL be globally unique within the registry
- SHALL remain stable once published

Each owner entry SHALL include:

```
<owner-id>:
  contact: "<primary contact email or individual>"
  website: "<canonical public URL>"
  organization: "<legal or operating name>"
  description: "<concise description of domain or responsibility>"
```

Owners are responsible for:
- Maintaining schema documentation
- Reviewing version changes
- Coordinating breaking updates
- Responding to dependency impacts

Changing an owner of an existing vocabulary word SHALL require explicit
review.

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

For broader change-process rules (PR structure, validation gates, ownership
transfer), see [../governance.md](../governance.md).
