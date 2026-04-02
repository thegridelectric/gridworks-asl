# Sema

Sema is a vocabulary registry for structured messages exchanged between independent systems.

It defines versioned **types, enums, and formats** expressed as JSON Schema. These schemas act as boundary contracts: they make the structure and semantics of serialized messages explicit and mechanically verifiable.

Sema applies only at **system boundaries.** It governs the structure and meaning of JSON messages exchanged between applications, but does not prescribe runtime architecture, database design, or internal object models.

The vocabulary defined in this repository allows systems developed by different teams to coordinate safely while evolving independently.

Because the vocabulary is machine-readable end-to-end — schemas, registry metadata, and dependency graphs — the same contracts can be used by humans and automated tools. Code generators, validators, and AI-assisted development environments can all reason from the same definitions of types and semantics.

The full technical specification is available at:
**[Sema Specification v1.0](https://schemas.electricity.works/sema/specification/1.0)**


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

## Vocabulary Snapshots

Instead of distributing a shared runtime package, Sema produces **self-contained vocabulary snapshots**.

A snapshot is a `sema/` directory committed into a repository. It contains a fully resolved subset of the Sema vocabulary — including all types, enums, formats, and their dependencies — along with the tooling needed to work with them locally.

Example structure:


## Example

A Sema type defines the structure of a serialized message. Each message explicitly declares its identity using `TypeName` and `Version`.

Example message::

```json
  {
    "Watts": 1500, 
    "TypeName": "power.watts", 
    "Version": "000"
  }
```
This message can be validated mechanically using the schema identified by:

```
https://schemas.electricity.works/types/power.watts/000
```

In generated  language bindings, the same message can be constructed using the corresponding type:

```python
power = PowerWatts(
    Value=1500,
    TypeName="power.watts",
    Version="000",
)
```
Because the contracts are explicit and versioned, systems can evolve their message vocabularies without breaking existing integrations.

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
Subcommands: reverse, seed, info
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

### Seed and Snapshot Generation

Sema supports generating **self-contained vocabulary snapshots** from a small set of initial targets.

A seed request defines the starting vocabulary:

```yaml
initial_targets:
  - "analytics.channel.gt:000"
  - "synced.readings.bundle:000"
```
From this, Sema tooling:
 1. Computes the **transitive dependency closure**
 2. Resolves all required formats, enums, and types
 3. Produces a complete, self-contained vocabulary snapshot

TODO: ELEVATE THE EXPLANATION OF WHAT THE sema/ folder IS IN A WORKING DIRECTORY

### Local Reasoning and AI Support

Sema is designed to support local semantic reasoning.

All vocabulary definitions, metadata, and dependency graphs are available locally:

  - schemas
  - registry metadata
  - dependency closure
  - reverse dependency relationships

This enables:

  - offline validation
  - code generation
  - AI-assisted reasoning over schema semantics

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

To propose a new vocabulary word or version:

1. Check `registry.yaml` to confirm the name is available
2. Add the new definition and registry entry
3. Submit a pull request

See the **Vocabulary Registration Process**(docs/rules_and_guidelines.md#vocabulary-registration-process) for full details.

Questions and proposals are welcome via GitHub issues.
