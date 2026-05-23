# Sema Specification — Governance

This sub-spec covers ownership responsibilities, vocabulary naming
discipline, registration, the canonical change process, conflict
resolution, and reserved namespaces.

Read [primary.md](primary.md) for core principles.

## Governance Position

This document defines the structural and evolutionary rules of Sema.

When conflicts arise between implementation and specification:

- The specification governs.
- Implementations SHALL be corrected.

(For runtime correctness conflicts among schema / registry / spec, see
the *Source precedence* section of [primary.md](primary.md#source-precedence).)

## Ownership Responsibilities

Each vocabulary word declared in `registry.yaml` SHALL have exactly one
owner listed in `owners.yaml`. (For `owners.yaml` structure, see
[registry/structure.md — owners.yaml](registry/structure.md#ownersyaml--vocabulary-ownership-registry).)

Owners are responsible for:

- Maintaining schema correctness and documentation
- Reviewing and approving version changes
- Ensuring evolution rules are followed
- Coordinating dependency impacts when introducing new versions
- Responding to reasonable community questions regarding semantics

Owners SHALL NOT:

- Publish breaking changes without incrementing version
- Modify historical versions in ways that alter validation behavior
- Transfer ownership without registry update

(For ownership transfer mechanics, see
[registry/types.md — Ownership Transfer](registry/types.md#ownership-transfer).)

## Vocabulary Naming Discipline

Sema supports a federated vocabulary model. Registration establishes
uniqueness and governance — not universal adoption.

Owners SHALL select names that reflect clear semantic intent and avoid
collision with common primitives (e.g., `uuid`, `id`, `value`). Namespace
scope signals ownership, not ecosystem authority.

This principle is especially important for enums, which define semantic
taxonomies. Organization-specific taxonomies SHOULD be published under
organization-scoped prefixes (e.g., `gw.g.node.class`).

The registry maintainer MAY request renaming prior to publication to
prevent excessive namespace capture or long-term ambiguity.

## Reserved Namespaces

Certain top-level namespace prefixes MAY be reserved in the future to
support cross-cutting behavior, forward compatibility, or governance
coordination.

At present, no namespace prefixes are formally reserved.

As ecosystem experience grows, reserved namespaces — if introduced —
SHALL be documented in this section and applied prospectively. Previously
registered vocabulary SHALL NOT be retroactively restricted.

Namespace reservation is expected to be rare and justified by clear
interoperability requirements.

## Vocabulary Registration Process

You can certainly use these ideas on your own within your organization
(or fork this repo). If you are in the electric grid balancing ecosystem,
we strongly encourage you to contribute your words to Sema.

### How to Add New Vocabulary

1. **Search existing vocabulary** — Check `registry.yaml` to make sure
   nobody owns this word yet.
2. **Fork and create PR** — Add yourself to `owners.yaml` and update
   `registry.yaml` with your new vocabulary.
3. **Send us an email** — Let us know at
   `gridworks@gridworks-consulting.com`.

## Change Process

All vocabulary changes SHALL be made through pull requests that:

1. Update the relevant schema file
2. Update `registry.yaml`
3. Update dependencies (if applicable)
4. Include a clear `summary` for new versions

For versioned types:

- The `summary` SHALL describe the change relative to the previous
  version.
- The `latest_version` field SHALL be updated.

Changes MUST pass:

- Structural validation
- Dependency validation
- Registry consistency checks

This is the single canonical Change Process for the Sema specification.

## Conflict Resolution

If ambiguity or dispute arises regarding:

- Semantic interpretation
- Versioning requirements
- Dependency correctness

The resolution order SHALL be:

1. The schema file for the relevant version
2. `registry.yaml`
3. This document

Schema validation behavior always governs runtime correctness. Registry
metadata governs lifecycle and discovery.
