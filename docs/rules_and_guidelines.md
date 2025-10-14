# GridWorks ASL Rules and Guidelines


## Table of Contents

- [Some Simple and Important Rules](#some-simple-and-important-rules)
- [Constitutional Documents as Specifications](#constitutional-documents-as-specifications)
- [Registry Structure](#registry-structure)
- [Vocabulary Components](#vocabulary-components)
- [Vocabulary Registration Process](#vocabulary-registration-process)
- [Evolution Guidelines](#evolution-guidelines)
- [Governance](#governance)



## Some Simple and Important Rules

GridWorks ASL serialized messages are all JSON.  We go through these rules in detail in the [Vocabulary Components](#vocabulary-components) section below. But here are a few simple and important rules so you get the flavor.

**1. Every vocabulary component has a name** using `left.right.dot` format:
- Formats: `uuid4.str`, `utc.seconds`
- Enums: `relay.state`, `sh.actor.role` 
- Types: `power.watts`, `channel.readings`

**2. All serialized fields must use CamelCase** (recursively through all nested structures):
```json
✅ Valid:
{"Bar": "bar", "TypeName": "foobar", "FooList": [{"Foo": "foo", TypeName: "foo"}]}

❌ Invalid (will be rejected, "foo" not CamelCase):  
{"Bar": "bar", "TypeName": "foobar", "FooList": [{"foo": "fools", TypeName: "foo"}]}
```

**3. Every type includes a TypeName field which must have its name as the value**:
```json
✅ Valid example of a power.watts type:
{"Watts": 3723, "TypeName": "power.watts", "Version": "000"}

❌ Invalid
{"Watts": 3723}
```

## Constitutional Documents as Specifications

Our schema specifications serve as **living constitutional documents** - machine-readable contracts about shared vocabulary that everything else builds from:

- **Machine-readable specifications** that can be used to generate clean, idiomatic code in any language
- **Versioned artifacts** with clear ownership and evolution paths  
- **Format refinements** that encode domain knowledge (naming conventions, hierarchical structures, time representations)
- **Human-readable documentation** that captures the intention behind the structure
- **Dependency tracking** that prevents breaking changes from cascading unexpectedly

These aren't rigid constraints but **flexible foundations** - constitutional agreements that enable rather than limit creative expression.

These specifications are written as **JSON Schema in YAML**:

- **Industry standard** with mature code generators in all major languages
- **Rich validation capabilities** - patterns, formats, constraints, conditional logic
- **Extension support** - `x-*` fields for custom metadata and tooling hints
- **Human-readable** - excellent for git diffs, supports comments, clear structure
- **Transport-agnostic** - works equally well with MQTT, HTTP, WebSockets, file systems
- **Perfect for granular adoption** - pick exactly the types you need, ignore the rest

## Registry Structure

All available vocabulary is listed in the `registry.yaml` file. The `owners.yaml` has additional information about entities who own vocabulary words. Each vocabulary word
is either a named type, an enum or a format. Each word has its own `.yaml` specification in 
the appropriate sub-folder:
```
 type_definitions/  
│   ├── registry.yaml  
│   ├── owners.yaml 
│   ├── schemas/  # named types
│   ├── formats/
│   └── enums/
```

**`owners.yaml`** - Centralized registry for schema owners:
```yaml
gridworks-energy:
  contact: gridworks@gridworks-consulting.com
  website: https://gridworks.energy
  organization: "GridWorks Energy LLC"
  description: "Transactive energy infrastructure and thermal storage systems"

microerapower:  
  contact: Stephanie Benson <smb@microerapower.com>
  website: https://microerapower.com
  organization: "MicroEra Power"
  description: "Distributed energy resource management"
```

**`registry.yaml`** - Vocabulary registry with proper ordering:
```yaml
metadata:
  registry_version: "1.0"
  last_updated: "2025-06-24T10:30:00Z"
  maintainer: "gridworks-energy"

formats:        # Alphabetical within section
  handle.name: # ...
  left.right.dot: # ...
  spaceheat.name: # ...
  utc.milliseconds: # ...
  utc.seconds: # ...
  uuid4.str: # ...

enums:          # Alphabetical within section
  log.level: # ...
  sh.actor.role: # ...

types:          # Alphabetical within section  
  channel.config: # ...
  power.watts: # ...
  spaceheat.node.gt: # ...
```

**Ordering Rules for registry.yaml:**
1. **Top-level sections**: `formats` → `enums` → `types` (dependency flow)
2. **Within sections**: Alphabetical order (easy navigation)
3. **Versions**: Newest first (reverse chronological)

## Vocabulary Components

### 1. Formats

**Purpose**: Define validation patterns for primitive types.

**Naming**: Use `left.right.dot` format (e.g., `uuid4.str`, `utc.seconds`)

**Required Registry Fields:**
```yaml
uuid4.str:
  owner: gridworks-energy              # Required - must exist in owners.yaml
  stable: true                         # Required - boolean
  schema_file: formats/uuid4.str.yaml  # Required
  created: "2024-06-24T08:00:00Z"      # Required
  description: "UUID4 string format"   # Required
```

**Example**: See [formats/uuid4.str.yaml](formats/uuid4.str.yaml) for a complete format definition.

### 2. Enums

**Purpose**: Define controlled vocabularies.

**Example**: See [enums/spaceheat.telemetry.name.005.yaml](enums/spaceheat.telemetry.name.005.yaml) for a complete enum definition.

**All enum files MUST include these required fields:**

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"    # Required
title: "exact.enum.name"                                  # Required - matches registry name
type: "string"                                            # Required - enums are strings
description: "Clear description"                          # Required
enum: ["Value1", "Value2", "DefaultValue"]               # Required - array of values
default: "DefaultValue"                                   # Required - must be one of enum values

x-gridworks:
  owner: "gridworks-energy"        # Required
  version: "007"                   # Required  
  value_descriptions:              # Optional but recommended
    "Value1": "Description..."
```

**Evolution Rules:**
- **Additive only** - New enum versions can only add values, never change or remove existing values
- **Immutable default** - The default value cannot change across versions

*These constraints enable backwards compatibility in distributed systems: the static default value provides a safe fallback for unknown enum values, while never removing values ensures older code continues to work with newer vocabularies.*

### 3. Types (Schemas)

**Purpose**: Define complex data structures.

**Naming**: Use `left.right.dot` format (e.g., `spaceheat.node.gt`, `power.watts`)

**Example**: See [schemas/spaceheat.node.gt.200.yaml](schemas/spaceheat.node.gt.200.yaml) for a complete type definition.

**Required Registry Fields:**
```yaml
spaceheat.node.gt:
  current_version: "200"               # Required for versioned types
  owner: gridworks-energy              # Required
  stable: true                         # Required  
  versioning_strategy: "literal"       # Required: "none", "literal", or "string"
  description: "SpaceHeat node representation"
  
  versions:
    "200":                             # Newest first
      schema_file: schemas/spaceheat.node.gt.200.yaml  # Required
      created: "2024-06-24T08:00:00Z"                  # Required
      stable: true                                     # Required
      dependencies:                                    # Required
        direct: ["sh.actor.class:000", "spaceheat.name:000", "uuid4.str:000"]
        all: ["sh.actor.class:000", "spaceheat.name:000", "uuid4.str:000"]
```


**Type Versioning Strategies**

Restrictions on types with strategy `none`:
- Properties MUST be primitive types or formats only
- NO references to other versioned ASL types
- NO Version field in schema


If Version exists, the format must be a  3 digit numeral: `"000"`, `"001"`, `"002"`. If the versioning_strategy is `literal` in the `registry.yaml` then  in the type's `.yaml`, Version is "const"

```  
  properties:
   [...]
    Version:
      const: "000"
```

And if the versioning_strategy is `string` in the `registry.yaml` then the Version is "string"



**Format references:**
```yaml
properties:
  NodeId:
    type: string
    format: uuid4.str         # Simple format name
```

**Schema references:**  
```yaml
properties:
  ChannelReadings:
    type: array
    items:
      $ref: "https://schemas.gridworks.energy/schemas/channel.readings.002"
```

**Enum references:**
```yaml
properties:
  ActorRole:
    $ref: "https://schemas.gridworks.energy/enums/sh.actor.role.000"
```

## Special Patterns and Reserved Namespaces

### Event Type Namespace: `gridworks.event.*`

The namespace `gridworks.event.*` is reserved for event types that require special handling in message processing systems. This pattern enables forward compatibility - systems can recognize and handle unknown event types gracefully rather than failing.

**Why this matters:**
- Distributed systems evolve at different rates
- New event types shouldn't break older deployments  
- Events often carry diagnostic or monitoring data that can be safely ignored if not understood

**Implementation requirements:**
When a decoder encounters an unknown type name starting with `gridworks.event.`:
1. It MUST NOT raise an error
2. It SHOULD decode the message as a generic event container (e.g., `AnyEvent`)
3. It SHOULD preserve all fields for potential logging or pass-through

**Example:**
```python
# System A sends a new event type
{"TypeName": "gridworks.event.battery.soc", "MessageId": "...", "StateOfCharge": 0.85}

# System B (older) doesn't know this type but handles it gracefully:
# - Decodes as AnyEvent
# - Logs the unknown event
# - Continues processing other messages
```
**Note** This pattern is specific to `gridworks.event.*`. Other type names like `report.event` do not receive this special treatment. If you're creating monitoring, diagnostic, or system events that should be forward-compatible, use the `gridworks.event.*` namespace.

## Vocabulary Registration Process

 You can certainly use these ideas on your own within your organization (or fork this repo). If you are in the electric grid balancing eco-system, we strongly encourage you to contribute your words to this ASL.

### How to Add New Vocabulary

1. **Search existing vocabulary** - Check [registry.yaml](type_definitions/registry.yaml) to make sure nobody owns this word yet
2. **Fork and create PR** - Add yourself to [owners.yaml](type_definitions/owners.yaml) and update [registry.yaml](type_definitions/registry.yaml) with your new vocabulary
3. **Send us an email** - Let us know at gridworks@gridworks-consulting.com

We're in the early days and excited to hear from you!

### Stability Promotion

Vocabulary is available for others to download if and only if it is stable.

You can request `stable: true` status once:
- The json specifications pass all the rules
- You've worked with us to add it to the à la carte menu (will happen by code gen soon)



## Evolution Guidelines


1. **Announce** changes in advance
2. **Support** old versions during transition. Deprecated versions: change to `stable: false`
3. **Document** migration path clearly
4. **Test** compatibility across implementations

Also, we encourage you to wait on requesting `stable: true` until you've used the vocabulary in real implementations, and verified that the API validation works at this site works as you intend.


## Governance

### Ownership Responsibilities

**Type owners must:**
- Maintain schema documentation
- Respond to community questions  
- Follow evolution guidelines
- Coordinate breaking changes
- Support migration paths

### Change Process

1. **Propose** changes via PR
2. **Review** by type owner
3. **Validate** against rules
4. **Test** compatibility
5. **Merge** when approved

### Constitutional Authority

This document is the **authoritative source** for ASL rules. When disputes arise about vocabulary evolution, this document provides the resolution framework.
