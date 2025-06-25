# GridWorks ASL Rules and Guidelines

*Constitutional document for GridWorks Application Shared Languages*

This document defines the rules, standards, and processes for creating and maintaining shared vocabulary in the GridWorks ASL ecosystem. **Following these rules is required before any vocabulary component can be marked `stable: true`.**

## Technical Architecture

### Why JSON Schema in YAML

**JSON Schema in YAML** provides the optimal foundation for shared vocabulary because:

- **Industry standard** with mature code generators in all major languages
- **Rich validation capabilities** - patterns, formats, constraints, conditional logic
- **Extension support** - `x-*` fields for custom metadata and tooling hints
- **Human-readable** - excellent for git diffs, supports comments, clear structure
- **Transport-agnostic** - works equally well with MQTT, HTTP, WebSockets, file systems
- **Perfect for granular adoption** - pick exactly the types you need, ignore the rest

This choice eliminates the "framework lock-in" problem that plagues many integration approaches. Teams can generate exactly the code they need in their preferred language without adopting anyone else's architectural decisions.

## Registry Structure

### Required Files

**`owners.yaml`** - Centralized registry for owners of schema:
```yaml
# e.g. 
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

**Ordering Rules:**
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

**Example Format Definition:**
```yaml
# formats/uuid4.str.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.gridworks.energy/formats/uuid4.str"

title: "uuid4.str"
type: string
pattern: ^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$

examples:
  - "6ba7b810-9dad-11d1-80b4-00c04fd430c8"

x-gridworks:
  owner: "gridworks-energy"
  use_cases: ["Component IDs", "Message IDs"]
```

### 2. Enums

**Purpose**: Define controlled vocabularies.

**Naming**: Use `left.right.dot` format (e.g., `sh.actor.role`, `log.level`)

**Required Registry Fields:**
```yaml
sh.actor.role:
  current_version: "000"               # Required for versioned enums
  owner: gridworks-energy              # Required  
  stable: true                         # Required
  versioning_strategy: "literal"       # Required: "none", "literal", or "string"
  description: "Actor roles for GridWorks SpaceHeat systems"
  
  versions:
    "000":
      schema_file: enums/sh.actor.role.000.yaml    # Required per version
      created: "2024-06-24T08:00:00Z"              # Required per version
      stable: true                                 # Required per version
      dependencies:                                # Required per version
        direct: []
        all: []
```

**Example Enum Definition:**
```yaml
# enums/sh.actor.role.000.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://schemas.gridworks.energy/enums/sh.actor.role.000"

title: "sh.actor.role"
type: string
enum:
  - "NoActor"
  - "Scada"
  - "PowerMeter" 
  - "Relay"
  # ...

default: "NoActor"

x-gridworks:
  owner: "gridworks-energy"
  version: "000"
  stable: true
```

### 3. Types (Schemas)

**Purpose**: Define complex data structures.

**Naming**: Use `left.right.dot` format (e.g., `spaceheat.node.gt`, `power.watts`)

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
        direct: ["sh.actor.role:000", "spaceheat.name:000", "uuid4.str:000"]
        all: ["sh.actor.role:000", "spaceheat.name:000", "uuid4.str:000"]
    "110":                             # Previous versions
      # ... similar structure
```

## Versioning Strategies

### Strategy: `"none"` (Versionless)

**Use for**: Simple operational messages (ping, ack, error)

**Restrictions**:
- **Properties MUST be primitive types or formats only**
- **NO references to other versioned ASL types**  
- **NO Version field in schema**

**Registry structure**:
```yaml
ping:
  owner: gridworks-energy              # Required
  stable: true                         # Required
  versioning_strategy: "none"          # Required
  schema_file: schemas/ping.yaml       # Required (at type level)
  created: "2024-06-24T08:00:00Z"      # Required (at type level)
  description: "Simple ping message"
```

**Example versionless schema**:
```yaml
# schemas/ping.yaml
type: object
properties:
  FromGNodeAlias:
    type: string
    format: left.right.dot
  TimeUnixS:
    type: integer
    format: utc.seconds
  TypeName:
    type: string
    const: "ping"
required: ["FromGNodeAlias", "TimeUnixS", "TypeName"]
# Note: No Version field
```

### Strategy: `"literal"` (Strict Versioning)

**Use for**: Configuration types, system structure definitions

**Requirements**:
- **Version field MUST be Literal type in generated code**
- **Exact version match required**
- **Breaking changes require new version**

**Example**:
```python
class NodeGt(BaseModel):
    Version: Literal["200"] = "200"  # Strict version
```

### Strategy: `"string"` (Flexible Versioning)

**Use for**: Most operational types

**Requirements**:
- **Version field is string with default**
- **Backwards compatible evolution preferred**
- **Consumers can handle version mismatches gracefully**

**Example**:
```python  
class ReportGt(BaseModel):
    Version: str = "003"  # Flexible string
```

## Required Fields Reference

### All Vocabulary Components
- `owner` - Must exist in owners.yaml
- `stable` - Boolean (true/false)
- `description` - Human-readable description

### Formats (always versionless)
- `schema_file` - Path to format definition  
- `created` - ISO timestamp when established

### Versioned Components (Enums, Types)
- `current_version` - Latest stable version (3 digits)
- `versioning_strategy` - "literal" or "string"
- Per-version fields:
  - `schema_file` - Path to version-specific schema
  - `created` - ISO timestamp when version created
  - `stable` - Boolean for this version
  - `dependencies.direct` - Direct dependencies array
  - `dependencies.all` - All transitive dependencies array

### Versionless Types (versioning_strategy: "none")
- `schema_file` - Path to schema (at type level)
- `created` - ISO timestamp (at type level)

## File Standards

### Schema File Standards (Complex Types)

**All schema files MUST include these required fields:**

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"    # Required
$id: "https://schemas.gridworks.energy/schemas/type.name.version"  # Required
title: "exact.type.name"                                  # Required - matches registry name
type: "object"                                            # Required
description: "Clear description of what this type represents"  # Required

properties:                                               # Required for object types
  TypeName:
    type: string
    const: "exact.type.name"                             # Required - must match title/registry
    description: "Type identifier"
    
  # Version field requirements by versioning strategy:
  Version:
    # For versioning_strategy: "literal"
    type: string
    const: "200"                                         # Required - exact version
    
    # For versioning_strategy: "string"  
    type: string
    default: "003"                                       # Required - default version
    
    # For versioning_strategy: "none" - NO Version field
    
  # All other properties MUST have:
  PropertyName:
    type: "string"                                       # Required - every property needs type
    description: "What this field represents"            # Required

required: ["TypeName"]                                   # Required - array of mandatory fields
additionalProperties: true                               # Required - explicit true/false

x-gridworks:                                            # Optional but recommended
  owner: "gridworks-energy"
  version: "200"
  examples:
    basic_example:
      TypeName: "exact.type.name"
      Version: "200"
```

**Dependencies per version** (required in registry.yaml):
```yaml
# In registry.yaml for each version
versions:
  "200":
    schema_file: schemas/spaceheat.node.gt.200.yaml
    created: "2024-06-24T08:00:00Z"
    stable: true
    dependencies:                                        # Required per version
      direct: ["sh.actor.role:000", "spaceheat.name:000"]  # Required - direct references
      all: ["sh.actor.role:000", "spaceheat.name:000"]     # Required - all transitive deps
```

### Enums File Standards

**All enum files MUST include these required fields:**

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"    # Required
$id: "https://schemas.gridworks.energy/enums/enum.name.version"  # Required
title: "exact.enum.name"                                  # Required - matches registry name
type: "string"                                            # Required - enums are strings
description: "Clear description of what this enum represents"  # Required

enum:                                                     # Required - array of values
  - "Value1"
  - "Value2"
  - "DefaultValue"

default: "DefaultValue"                                   # Required - must be one of enum values

x-gridworks:                                             # Optional but recommended
  owner: "gridworks-energy"
  version: "000"
  stable: true
  use_cases: ["Where this enum is used"]
  categories:                                            # Optional - grouping for large enums
    group1: ["Value1", "Value2"]
```

**No dependencies** - Enums are primitive vocabularies and don't reference other ASL types.

### Formats File Standards

**All format files MUST include these required fields:**

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"    # Required
$id: "https://schemas.gridworks.energy/formats/format.name"  # Required
title: "exact.format.name"                                # Required - matches registry name
type: "string"                                            # Required - formats validate strings
description: "Clear description of what this format validates"  # Required

pattern: "^[a-z][a-z0-9]*(\.[a-z0-9]+)*$"               # Required - regex validation pattern

examples:                                                 # Required - valid examples
  - "valid.example.1"
  - "another.valid.example"

counterexamples:                                         # Optional but recommended
  - "Invalid-Example"     # why: uppercase not allowed
  - "123.starts.number"   # why: cannot start with number

x-gridworks:                                             # Optional but recommended
  owner: "gridworks-energy"
  use_cases: ["Node names", "Type identifiers"]
```

**No dependencies or versions** - Formats are versionless primitives.

### Reference Patterns

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

### Naming Conventions

**All ASL serialized fields use CamelCase:**
```json
✅ Valid:
{"FromGNodeAlias": "hw1.isone", "TypeName": "power.watts"}

❌ Invalid:  
{"from_gnode_alias": "hw1.isone", "type_name": "power.watts"}
```

## Dependencies

### Direct Dependencies
List types that this schema directly references.

### All Dependencies  
List all transitive dependencies (direct + their dependencies).

**Example:**
```yaml
# report depends on channel.readings, which depends on spaceheat.name
report:
  dependencies:
    direct: ["channel.readings:002", "machine.states:001"]
    all: ["channel.readings:002", "machine.states:001", "spaceheat.name:000", "utc.milliseconds:000"]
```

## Evolution Guidelines

### Stability Lifecycle

1. **`stable: false`** - Development phase
   - API may change
   - Not recommended for production
   - Must follow all rules before marking stable

2. **`stable: true`** - Production ready
   - Breaking changes follow governance process
   - Backwards compatibility commitment
   - Full rule compliance verified

### Version Evolution

**Patch changes** (`001` → `002`):
- Add optional fields
- Clarify documentation  
- Fix non-breaking validation

**Minor changes** (`001` → `010`):
- Change validation rules
- Add required fields with defaults
- Deprecate fields

**Major changes** (`001` → `100`):
- Remove fields
- Change field types
- Breaking validation changes

### Migration Process

1. **Announce** changes in advance
2. **Support** old versions during transition
3. **Document** migration path clearly
4. **Test** compatibility across implementations

## Code Generation

### Boundary Markers

Generated code uses **CamelCase for ASL types** to provide intentional cognitive friction:

```python
# Clear ASL boundary markers
node.FromGNodeAlias  # ← ASL type field
node.ComponentId    # ← ASL type field

# vs internal application code  
node.component_id   # ← Internal Python style
node.from_alias     # ← Internal Python style
```

This "foreignness" reminds developers they're working with shared protocol data, not internal application state.

### Generated Structure

Seed repositories include:
- **Named types** implementing schemas
- **Enums** with proper defaults  
- **Format validators** for primitive types
- **Dependency resolution** for complex types

## Validation Requirements

### Before `stable: true`

All vocabulary components MUST:

1. **Follow naming conventions** (left.right.dot)
2. **Have valid owner** (exists in owners.yaml)
3. **Include all required registry fields**
4. **Validate against JSON Schema** 
5. **Resolve all dependencies** correctly
6. **Include working examples**
7. **Pass compatibility tests**

### Tooling Support

```bash
# Validate registry structure
asl validate registry.yaml --check-owners

# Verify schema compliance  
asl validate schemas/ --check-required-fields

# Test dependency resolution
asl validate registry.yaml --check-dependencies

# Ensure versioning strategy consistency
asl validate types/ --check-versioning-strategy
```

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

**Remember**: These rules exist to enable collaboration, not prevent it. They create the shared foundation that allows organizations to build sophisticated systems while maintaining interoperability.

---

*Following these guidelines ensures your vocabulary contributions enhance the ASL ecosystem while preserving organizational sovereignty and enabling ecosystem growth.*