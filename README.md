# Sema

Sema is a vocabulary registry for structured messages exchanged between independent systems.

It defines versioned **types, enums, and formats** expressed as JSON Schema. These schemas act as boundary contracts: they make the structure and semantics of serialized messages explicit and mechanically verifiable.

Sema applies only at **system boundaries.** It governs the structure and meaning of JSON messages exchanged between applications, but does not prescribe runtime architecture, database design, or internal object models.

The vocabulary defined in this repository allows systems developed by different teams to coordinate safely while evolving independently.

Because the vocabulary is machine-readable end-to-end — schemas, registry metadata, and dependency graphs — the same contracts can be used by humans and automated tools. Code generators, validators, and AI-assisted development environments can all reason from the same definitions of types and semantics.

The full technical specification is available at:
**[Sema Specification v1.0](https://schemas.electricity.works/sema/specification/1.0)**


## Why this matters

When shared message structures evolve slowly and unsafely, the vocabulary
itself becomes the constraint. Small changes — adding a field, extending
an enum, clarifying a concept — turn into coordinated deployments,
version negotiations, or breaking migrations across multiple systems.
Sema treats shared vocabulary as a first-class, versioned artifact so
systems can evolve independently while continuing to communicate
reliably.

This approach provides several practical benefits:

- **Independent evolution** — vocabulary changes are versioned at the
  level of individual words; new types or fields can be introduced
  without forcing coordinated migrations across unrelated systems.
- **Language neutrality** — definitions are expressed as JSON Schema and
  can generate bindings in multiple programming languages.
- **Clear system boundaries** — shared vocabulary is defined once and
  reused across systems; application code is free to implement its own
  internal models and architecture.
- **Open collaboration** — vocabulary evolves through contributions to
  the registry rather than through centralized API ownership.

The vision: make shared vocabulary **explicit, portable, and evolvable**,
so distributed systems can coordinate while remaining autonomous.


## Core Vocabulary Model

Sema defines three kinds of vocabulary words:

 - **Formats** — reusable validation constraints for primitive values
 - **Enums** — controlled vocabularies for semantic categories
 - **Types** — structured messages exchanged between systems

Each word has a globally unique name using the left.right.dot convention and is registered in the Sema registry.

Examples:
```
formats:
  uuid4.str
  utc.seconds

enums:
  market.price.unit
  base.g.node.class

types:
  bid
  report
```

Types are the primary message contracts exchanged between applications. Every serialized type declares its identity explicitly:

```
{
  "Watts": 3723,
  "TypeName": "power.watts",
  "Version": "000"
}
```
This explicit identity allows messages to be validated, composed, and interpreted consistently across independent systems.

All vocabulary definitions are expressed as JSON Schema, making them language-neutral and suitable for automated validation and code generation.

For the full rules governing vocabulary structure, versioning, and registry behavior, see the [Sema Specification](https://schemas.electricity.works/sema/specification/1.0).

## The Sema Registry and Generator

This repository contains the **Sema vocabulary registry and generation tooling.**

Vocabulary definitions are authored as YAML schema files and registered in registry.yaml. Each vocabulary word — format, enum, or type — is assigned a **canonical schema identifier** hosted under:

```
https://schemas.electricity.works/
```
Examples:

```
https://schemas.electricity.works/formats/uuid4.str
https://schemas.electricity.works/enums/sh.actor.class/007
https://schemas.electricity.works/types/report/002
```


These URLs serve as the globally stable identifiers for Sema vocabulary and are used directly in `$ref` links within schemas and generated code.

## Adding a New Type

New Sema types are authored in two layers:

- the schema and registry metadata, which define the public contract
- optional runtime axiom templates, which contain hand-written validation logic

To add a type:

1. Add the schema YAML under `definitions/types/<type-name>/<version>.yaml`.
   Follow the type, versioning, dependency, enum, format, and axiom rules in
   [`spec/primary.md`](spec/primary.md) (the spec hub; per-kind
   spokes live under `spec/registry/` and `spec/authoring/`).

2. Add the type version to `definitions/registry.yaml`.
   Declare only direct dependencies. Use `structural` for `$ref` dependencies
   required by the schema and `axiom` for vocabulary used only by axiom logic.

3. If the schema declares `x-gridworks.axioms`, create the runtime axiom
   template stub:

   ```bash
   uv run sema runtime scaffold-axiom-template <type-name> <version>
   ```

   This writes a new file under
   `src/sema/tools/runtime_generation/templates/axioms/`. Existing templates
   are not overwritten. The generated stub includes formatted axiom docstrings
   from the schema and raises `NotImplementedError` until the validation logic
   is filled in.

4. Fill in the hand-written validation logic in the generated Jinja template.
   The Jinja template is the maintained source for custom runtime axiom code;
   runtime regeneration renders it into `src/sema/runtime/types/...`.
   Runtime axiom failures should identify the mechanical axiom number, such as
   `Axiom 1`. Tests for invalid examples should assert that number
   case-insensitively rather than matching semantic labels or full prose, since
   labels and wording are human-authored documentation.

5. Rebuild indexes and run validation:

   ```bash
   ./scripts/build_indexes.sh
   uv run pytest tests/registry tests/indexes/test_indexes_are_up_to_date.py
   ```

6. Regenerate the local runtime only when you are ready to update generated
   runtime files:

   ```bash
   uv run python scripts/regenerate_runtime.py
   ```

## Adding a New Version of a Type

When a versioned type gains a new version, the `<a> -> <b>` change delta is
recorded in **three coupled places** — touch one, reconcile all three:

- the upgrade template body **and** docstring
  (`src/sema/tools/runtime_generation/templates/upgrades/<type_snake>_<a>_to_<b>.py.jinja2`)
- `definitions/registry.yaml` → `types.<type>.versions.<b>.summary` — the
  prose change-list (kept a mirror copy of the upgrade docstring)
- `definitions/registry.yaml` → `types.<type>.versions.<b>.direct_dependencies`
  — the machine change-list

The docstring↔summary mirror is enforced by
`tests/registry/test_upgrade_summary_matches_template.py`. The rule the
upgrade body must satisfy: a nested sub-type whose version changes between
the outer type's `<a>` and `<b>` must be lifted via its own `.upgrade()`
(see [`spec/authoring/type-semantics.md`](spec/authoring/type-semantics.md)
"Nested Upgrades") — a dependency delta in the registry with no matching
lift in the body is the bug class this coupling exists to catch.

## Vocabulary Snapshots

Instead of distributing a shared runtime package, Sema produces **self-contained vocabulary snapshots**.

A snapshot is a `sema/` directory committed into a repository. It contains a fully resolved subset of the Sema vocabulary — including all types, enums, formats, and their dependencies — along with the tooling needed to work with them locally.

Example structure:

```
repo/
  sema/
    base.py
    codec.py
    property_format.py
    enums/
    types/
    definitions/
      registry.yaml
      formats/
      enums/
      types/
    indexes/
      dependency_closure.yaml
      reverse_dependencies.yaml
      lookup.yaml
      versions.yaml
    tests/
      test_property_format.py
```


A snapshot provides everything required to:

- validate messages
- construct typed objects
- analyze dependencies
- reason about schema semantics

All data required for these operations is available locally — no remote schema fetching is required.

Projects commit the generated `sema/` directory directly into their repository.

This approach provides:

- **repository independence** — each project carries its own validated vocabulary
- **no shared runtime dependency conflicts**
- **local visibility of message contracts and their semantics**

Vocabulary dependencies are resolved automatically. If a selected type references other types, enums, or formats, those dependencies are included in the snapshot.

 

## CLI and Local Tooling

Sema includes a CLI for working with vocabulary definitions, dependency graphs, and snapshot generation.

Run:
```
uv run sema info
```

Example output:
```
Sema CLI
Interface: textual
Subcommands: reverse, runtime, snapshot, info
```

### Reverse Dependency Analysis

The `reverse` command returns the **transitive reverse dependency closure** for a vocabulary word.
```
uv run sema reverse relay.actor.config 003
uv run sema reverse gw1.unit 001
uv run sema reverse left.right.dot
```

Rules:
- Types and enums MUST include a version
- Formats do not include a version

This is useful for:
- understanding impact of changes
- identifying downstream dependencies
- reasoning about schema evolution

---

### Vocabulary Selection and Snapshot Generation

Sema generates snapshots from a small set of initial targets.

A seed request defines the starting vocabulary. Use
[`template_seed_request.yaml`](template_seed_request.yaml) at the repository
root as the starting template.

```yaml
initial_targets:
  types:
    synced.readings.bundle: {}

    snapshot.spaceheat:
      include_all_versions: true

    layout.lite:
      versions: ["011", "013"]

  enums:
    relay.energization.state:
      versions: ["000"]
```

For each type or enum target:

- `{}` selects the latest registry version
- `include_all_versions: true` selects every registry-declared version
- `versions: ["011", "013"]` selects explicit versions; intermediate type versions are added during expansion

Build a snapshot in two steps:

```bash
uv run sema snapshot prepare template_seed_request.yaml
uv run sema snapshot build --package-name gjk
```

The prepare step:

- clears the existing `output/` directory
- computes the **transitive dependency closure**
- resolves all required formats, enums, and types
- writes definitions under `output/sema/definitions`
- writes restricted indexes under `output/sema/indexes`
- writes `output/sema/indexes/seed_expanded.yaml`
- records the original request as `output/sema/indexes/seed_request.yaml`, so the
  snapshot is self-describing and exactly replicable
- materializes `output/sema/indexes/local_names.yaml` from the seed request's
  `local_names` rules

Local (Python) class and module names are declared **in the seed request**, not
hand-edited. A `local_names` block sets `strip_prefixes` — leading dotted
segments dropped from each name — plus per-type `overrides` for special cases or
to resolve a collision:

```yaml
local_names:
  strip_prefixes: [gw1, gw]   # gw1.unit -> class Unit; gw.house0.layout -> House0Layout
                              # (gw108.* is untouched — its head is gw108, not gw1/gw)
  overrides:
    some.long.type.name: short.name
```

The keys remain canonical Sema names; the derived local names are
`left.right.dot`, and Python class/module names are derived from them. Local
names must be unique within a snapshot — a collision fails `prepare`, naming both
types so you can add an `override`. The dotted `TypeName` wire identity is never
affected; only the local class name is.

The build step:

- reads `output/sema/indexes/seed_expanded.yaml`
- reads `output/sema/indexes/local_names.yaml`
- writes the runtime snapshot under `output/sema`

The generated files under `output/sema` are intended to be copied into the
target repository under `src/<package-name>/sema`. The `--package-name` value is
used in generated imports, for example `from gjk.sema.enums import ...`.


### Local Reasoning and Indexes

Sema is designed to support **local semantic reasoning**.

Each snapshot includes an `indexes/` directory containing precomputed dependency and lookup data:

- `dependency_closure.yaml`
- `reverse_dependencies.yaml`
- `lookup.yaml`
- `versions.yaml`
- `seed_request.yaml`
- `seed_expanded.yaml`
- `local_names.yaml`

These indexes enable tools to reason about the vocabulary efficiently without recomputing graph relationships.

For example, the CLI command:

```
uv run sema reverse relay.actor.config 003
```

uses the reverse dependency index to compute the local transitive impact of a type.

Because these indexes are included in every snapshot, both humans and automated systems — including AI tools — can:

- analyze dependencies
- understand schema relationships
- reason about design decisions
- operate offline without external schema access

This makes the snapshot not just a validation artifact, but a **local semantic knowledge base**.

## Web Tooling
Sema is designed to be used with automated tooling that manages vocabulary selection, validation, and code generation.

Planned tools include:
 - **CLI** - a global version of the local CLI
 - **Validation API** — validate serialized messages against the Sema schemas
 - **Registry tools** — dependency analysis, version diffing, and registry consistency checks
 - **Web UI** — browse vocabulary and select types à la carte

These tools help ensure that Sema vocabulary remains mechanically verifiable and easy to adopt across independent repositories.


## Contributing

Sema vocabulary is developed in the open registry.

Vocabulary work happens on a topic branch cut from `dev` (one topic per
branch), returned to `dev` by pull request; nothing is authored on `dev`
directly.

To propose a new vocabulary word or version:

1. Check `registry.yaml` to confirm the name is available
2. Add the new definition and registry entry
3. Submit a pull request

See the [**Vocabulary Registration Process**](spec/governance.md#vocabulary-registration-process) for full details.

Questions and proposals are welcome via GitHub issues.
