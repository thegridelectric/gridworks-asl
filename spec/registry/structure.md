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

Every registry entry SHALL carry an explicit `status` field indicating its
lifecycle state. There is no default: a missing `status` is a
registry-validation error.

Allowed values:
- `"draft"` — not ready for use. Mutable; excluded from `latest_version`,
  the public registry surface, runtime generation, and snapshots.
- `"staging"` — in real use across repos while still mutable in place.
  Staging vocabulary is consumable by runtime generation and snapshots but
  SHALL run against dev brokers only — never hybrid, never production.
- `"published"` — immutable per this specification. Any semantic or
  validation change to a published definition SHALL be expressed through a
  new version. Published vocabulary is eligible for hybrid and production
  brokers and for serving at `https://schemas.electricity.works`.

Placement:

- For formats, versionless types, and literal enums, `status` appears on
  the word entry. Formats never stage: a format's status is `"draft"` or
  `"published"` only.
- For versioned enums and versioned types, `status` applies to individual
  version entries under `versions`.

A versioned enum or type MAY hold versions in different statuses at the
same time. In that case:

- `latest_version` SHALL identify the latest non-draft (staging or
  published) version
- Draft versions SHALL NOT be selected by `latest_version`
- Draft versions MAY be numerically greater than `latest_version`
- Tooling MAY expose draft versions only when explicitly requested

A published version's full dependency closure (structural and axiom) SHALL
itself be published — a published definition may not reference a staging
or draft word. Staging definitions may reference staging or published
words; nothing non-draft may reference a draft.

Draft and staging definitions SHALL NOT be served at
`https://schemas.electricity.works`. Draft definitions are additionally
excluded from public schema indexes. A staging definition's `$id` uses the
canonical (non-draft) URL: publication is a status change and a later
serving event, not a URL change. Draft schemas use the `/draft/` URL
segment.

For draft and staging definitions, `created` records the time the entry
was first added to the working registry. Promotion — draft to staging, or
staging to published — never changes `created`. From publication forward,
`created` is governed by the immutability rules for published definitions.

If a draft schema file appears under `definitions/`, it SHALL remain
parseable YAML and SHALL use the normal Sema schema file layout. Draft and
staging status relax immutability and may relax completeness checks
defined by tooling, but they do not permit malformed schema files.

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

## `frozen_at` Field

Registry word entries MAY include a `frozen_at` field marking the word's
version lineage as **closed** — the owner will cut no further versions.

`frozen_at`:

- SHALL appear only on a vocabulary **word** entry, never on a version entry
- SHALL be an RFC 3339 timestamp (seconds precision, UTC `Z`), per the
  Timestamp Rules above; its **presence** means the word is frozen, and it
  records when the lineage was closed
- is a **different axis** than `status`: `status` (`draft`/`published`)
  describes whether a *version* is published; `frozen_at` describes whether
  the *word* will gain new versions. A frozen word's existing versions remain
  exactly as published.

Semantics. A word with `frozen_at`:

- remains valid; its existing published versions stay decodable indefinitely
  (freezing is **not** deletion or deprecation of existing versions)
- SHALL NOT gain a new version: no version entry may carry a `created`
  timestamp later than `frozen_at` (authoring a new version after the freeze
  is a registry-validation error)
- is unaffected in its description fields — `frozen_at` gates *new versions*
  only; permitted description clarifications to existing published versions
  are governed by the normal immutability rules
- for structurally single-version words (versionless formats, literal enums,
  versionless types), which cannot gain versions anyway, `frozen_at` is a
  retirement *signal* rather than an additional gate

`frozen_at` is **orthogonal to `replaced_by`** and the two compose freely:

- a word MAY be frozen with no `replaced_by` (retire a concept with no
  successor)
- a word MAY carry `replaced_by` without being frozen (a migration window in
  which the old lineage is still maintained)
- when both are present, `replaced_by` names the preferred successor(s) while
  `frozen_at` closes the lineage; neither implies the other

There is no MUST coupling `replaced_by` to `frozen_at`; tooling MAY emit an
advisory warning when a `replaced_by` word is not also frozen.

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
