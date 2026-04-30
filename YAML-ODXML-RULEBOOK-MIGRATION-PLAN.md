# YAML → ODXML → Rulebook Migration Plan

## Purpose

Today this project has **two parallel implementations** of the same conceptual model — versioned formats, enums, types, and their dependencies:

- **Set A (legacy):** Airtable → `Airtable.xml` / `DataSchema.odxml` → XSLT-driven codegen under `code_gen/GridworksCore/`.
- **Set B (current source of truth):** hand-edited YAML registry under `definitions/`, with Python tools in `src/sema/tools/` building indexes under `indexes/`.

Neither implements the **Effortless Rulebook (ERB / CMCC v1)** schema. This plan defines the path to:

1. Make a rulebook (`./effortless-rulebook/effortless-rulebook.json`) the **top of the loop**.
2. Migrate the YAML registry into the rulebook losslessly.
3. Generate the YAML registry as a **downstream artifact** from the rulebook.
4. Eventually push the rulebook into Airtable so Airtable becomes the editor again.
5. Phase out the ODXML/XSLT pipeline as the rulebook absorbs every concept it modeled.

The end-state loop:

```
[Admin UI / Airtable]
        │
        ▼
effortless-rulebook.json  ◄── top of loop, git-versioned
        │
        ├─► effortless build → postgres schema + views + functions
        ├─► YAML registry emitter ──► definitions/*.yaml (artifact)
        └─► (future) codegen consumes rulebook views directly,
                     replacing ODXML + XSLT
```

---

## Guiding principles

These were settled in design discussion. They shape every choice below.

1. **Polymorphic with the YAML.** The migrator must round-trip YAML → rulebook → YAML losslessly (canonical-equivalent, not necessarily byte-equivalent).
2. **Snapshot = the rulebook file itself.** Versioning lives in git. Each emitted `effortless-rulebook.json` contains *every* `(Name, Version)` pair extant at that moment. No internal "rulebook version" record.
3. **Commit to structure on day one; defer columns.** Structural choices (parent/child tables, FK pinning, blob vs. row) are expensive to revisit; column additions are cheap. The day-one schema fixes structure even when the corresponding columns aren't populated yet.
4. **Model what's universal; escape-hatch the long tail.** Every field that appears across all (or nearly all) entities of a kind gets a real column. Anything that isn't universal — JSON-Schema exotica, custom upgrade logic, project-specific extensions — has a designated escape hatch (`RawJson`, `RawScript`, …) so the rulebook stays lossless without forcing every case into a declarative shape it doesn't fit.
5. **Correct now, not corrected later.** No flat-now-split-later, no blob-now-table-later. Pay the small upfront cost to get the shape right.

---

## Findings from the deep dive

Surveyed 69 type files, 38 enum files (32 enum names, 5 with multiple versions), 11 format files, plus `registry.yaml` and `owners.yaml`.

### Cross-reference rules

| Ref kind | Pinned to version? | Example |
|---|---|---|
| Type → Type | Yes (3-digit suffix) | `.../types/data.channel.gt/002` |
| Type → Enum | Yes (3-digit suffix) | `.../enums/gw1.actor.class/009` |
| Type → Format | No | `.../formats/uuid4.str` |

### Universal type-file features (100% of 69 type files)

- JSON-Schema 2020-12.
- `x-gridworks` extension block — at minimum `owner`, **almost always `axioms`**.
- `TypeName` and `Version` declared as `const` properties (identity markers, not real attributes).
- Explicit `additionalProperties: true|false` (56 closed / 13 open).

### Type-file features in significant minorities

| Feature | Count | Implication |
|---|---|---|
| `examples` array | 32/69 | child table |
| Inline nested object in array `items` | 3/69 | auto-promote to `TypeHelper` |
| `oneOf` polymorphic union | 1/69 | park in `RawJson` for v1; promote to first-class when n>1 |

### Universal enum-file features (38 files, 32 names)

- `enum:` array of string symbols.
- `default:` symbol.
- `x-gridworks: { owner, version }` (the `version` field is redundant with the file path; file path is canonical).
- 30/38 have `value_descriptions:` (per-symbol description map).
- 5 enum names have multiple versions (max 3: `gw1.actor.class` 009/010/011).

### Universal format-file features (11 files)

- `pattern` (regex), `minLength`, `maxLength`.
- `examples` and `counterexamples` arrays.
- `x-gridworks: { owner }`.

### What this changes from the original design sketch

- **`TypeAxioms` is day-one, not Tier 2.** 100% of type files carry axioms.
- **`EnumValues.Description` is day-one.** 79% of enums populate it.
- **Format pattern + bounds are flat columns**, not `RawJson`.
- **`TypeHelpers` table has rows on day one** (4 inline-nested cases need them).

---

## Six structural decisions (locked)

| # | Decision | Rationale |
|---|---|---|
| 1 | Inline nested objects (array `items`, `oneOf` branches) auto-promote to `TypeHelpers` with synthesized names | Codegen needs row-level access to nested attributes; ODXML's `TypeHelper` confirms the pattern; keeping these in `RawJson` would force a future blob-rip |
| 2 | `oneOf` polymorphic unions park in `TypeAttributes.RawJson` for v1; first-class modeling deferred until a second use case appears | Avoids overfitting to n=1; when a second case appears we'll see whether discrimination is structural or keyed and model accordingly. Round-trip stays lossless via blob; no consumer depends on row-level access today |
| 3 | Examples and counterexamples → child tables (`TypeExamples`, `FormatExamples`) | Stable row shape, queryable, admin-UI editable; only the example *body* is JSON |
| 4 | `TypeName` / `Version` `const` fields are auto-emitted from `(TypeVersion.Type.Name, TypeVersion.Version)`, not stored as `TypeAttribute` rows | They're identity markers; storing them duplicates state |
| 5 | Format columns: `Pattern`, `MinLength`, `MaxLength`, `Format`, `Description` + `RawJson` escape | Universal across format files; flat-and-queryable |
| 6 | The rulebook lives at `./effortless-rulebook/effortless-rulebook.json` (top-level), not the legacy 3.7 MB copy under `code_gen/GridworksCore/` | ERB convention; legacy file is ignored and removed after Set A is decommissioned |

---

## Day-1 rulebook schema (Tier 1)

**12 tables.** Sized to absorb every YAML feature losslessly while leaving room for ODXML's protocol/routing/CRUD dimensions to layer in later as additive columns or new tables.

### Table list

```
# Module 1 — Schema of record
Owners
Formats
FormatExamples
Enums
EnumVersions
EnumValues
Types
TypeVersions
TypeAttributes
TypeExamples
TypeAxioms
TypeHelpers
TypeHelperAttributes

# Module 2 — Version upgrades
Projections
ProjectionMappings
TypeUpgrades
TypeUpgradeOps
EnumUpgrades
EnumUpgradeMappings
```

(19 tables: 13 schema-of-record + 6 version-upgrade.)

### Schema details

#### `Owners`
| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; e.g. `gridworks-energy` |
| `Description` | string | |
| `Email` | string | |

#### `Formats`
| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; e.g. `uuid4.str` |
| `Owner` | FK→Owners | |
| `SchemaUrl` | string | from `$id` |
| `Title` | string | |
| `Description` | string | |
| `Pattern` | string | regex |
| `MinLength` | integer | nullable |
| `MaxLength` | integer | nullable |
| `JsonSchemaFormat` | string | nullable; the JSON-Schema `format` keyword if present |
| `Created` | datetime | from `registry.yaml` |
| `RawJson` | string | escape hatch for unmodeled JSON-Schema fields |

#### `FormatExamples`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=Format & "[" & Idx & (IsCounter ? "x]" : "]")` |
| `Format` | FK→Formats | |
| `Idx` | integer | preserves YAML ordering |
| `IsCounter` | boolean | true = counterexample |
| `Value` | string | the example string |
| `Description` | string | nullable; YAML inline comment if present |

#### `Enums`
| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; e.g. `gw1.actor.class` |
| `Owner` | FK→Owners | |
| `EnumType` | string | from `registry.yaml` (e.g. `versioned`) |
| `Description` | string | name-level (registry-level) description |
| `LatestVersion` (calc) | string | =MAX over EnumVersions.Version |

#### `EnumVersions`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=Enum & "/" & Version` |
| `Enum` | FK→Enums | |
| `Version` | string | e.g. `007` |
| `SchemaUrl` | string | from `$id` |
| `Title` | string | from `title:` |
| `Description` | string | version-specific description |
| `DefaultSymbol` | string | from `default:` |
| `Status` | string | nullable |
| `Created` | datetime | from `registry.yaml` versions block |
| `IsCurrent` (calc) | boolean | `=Version == Enum.LatestVersion` |

#### `EnumValues`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=EnumVersion & ":" & Symbol` |
| `EnumVersion` | FK→EnumVersions | |
| `Symbol` | string | the literal value, e.g. `Power` |
| `Idx` | integer | preserves YAML ordering |
| `Description` | string | from `value_descriptions` map |
| `IsDefault` (calc) | boolean | `=Symbol == EnumVersion.DefaultSymbol` |

#### `Types`
| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; e.g. `report` |
| `Owner` | FK→Owners | |
| `Title` | string | name-level title |
| `Description` | string | name-level description |
| `LatestVersion` (calc) | string | =MAX over TypeVersions.Version |
| `PythonClassName` | string | nullable; ODXML invariant — populated as Tier-2 absorbs ODXML data |
| `MakeDataClass` | boolean | nullable; same |
| `IsCac` | boolean | nullable; same |
| `IsComponent` | boolean | nullable; same |

#### `TypeVersions`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=Type & "/" & Version` |
| `Type` | FK→Types | |
| `Version` | string | e.g. `002` |
| `SchemaUrl` | string | from `$id` |
| `Title` | string | from `title:` |
| `Description` | string | version-specific description |
| `ExtraAllowed` | boolean | from `additionalProperties` |
| `Status` | string | nullable |
| `Created` | datetime | nullable |
| `IsCurrent` (calc) | boolean | `=Version == Type.LatestVersion` |
| `RawJson` | string | unmodeled top-level JSON-Schema fields (`if`/`then`/`else`, conditionals, etc.) |

#### `TypeAttributes`
The shape-of-record for every property declared on a `TypeVersion`. Polymorphic via mutually-exclusive FK columns + flags.

| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=TypeVersion & "." & AttributeName` |
| `TypeVersion` | FK→TypeVersions | |
| `AttributeName` | string | property key in JSON-Schema |
| `Idx` | integer | preserves YAML ordering |
| `Description` | string | |
| `IsRequired` | boolean | derived from parent `required` array |
| `IsList` | boolean | true if `type: array` |
| `PrimitiveType` | string | nullable: `string`, `integer`, `number`, `boolean`, `null` |
| `FormatRef` | FK→Formats | nullable |
| `EnumVersionRef` | FK→EnumVersions | nullable |
| `SubTypeVersionRef` | FK→TypeVersions | nullable |
| `HelperRef` | FK→TypeHelpers | nullable; for inline-nested-object items |
| `RawJson` | string | unmodeled JSON-Schema specifics, including `oneOf` bodies (v1) |

Polymorphism rule: at most one of `FormatRef` / `EnumVersionRef` / `SubTypeVersionRef` / `HelperRef` is non-null per row. If `IsList`, the FK refers to the *item* type. `oneOf` attributes are recognized at migration time and the entire `oneOf:` body is parked in `RawJson` for round-trip — no FK or flag is set. (Promotion to first-class is a Tier-2 expansion, see below.)

#### `TypeExamples`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=TypeVersion & "[" & Idx & "]"` |
| `TypeVersion` | FK→TypeVersions | |
| `Idx` | integer | preserves YAML ordering |
| `ExampleJson` | string | full instance example |

#### `TypeAxioms`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=TypeVersion & ".axiom" & Number` |
| `TypeVersion` | FK→TypeVersions | |
| `Number` | integer | from YAML `number:` |
| `AxiomName` | string | from YAML `name:` |
| `Statement` | string | from YAML `statement:` |

#### `TypeHelpers`
Non-versioned reusable subtypes — used for inline nested objects (array items, `oneOf` branches) auto-promoted by the migrator.

| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; synthesized: `<parent-type>.<context>` (e.g., `scada.control.capabilities.RelayNode`) |
| `Title` | string | from inline `description:` if present |
| `Description` | string | |
| `ExtraAllowed` | boolean | from inline `additionalProperties` |
| `OriginTypeVersion` | FK→TypeVersions | the type whose YAML body introduced this helper (round-trip provenance) |
| `OriginPath` | string | JSON-Pointer-ish path within origin (e.g., `/properties/RelayNodes/items`) — used to re-inline on YAML emit |

#### `TypeHelperAttributes`
| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=TypeHelper & "." & AttributeName` |
| `TypeHelper` | FK→TypeHelpers | |
| `AttributeName` | string | |
| `Idx` | integer | |
| `Description` | string | |
| `IsRequired` | boolean | |
| `IsList` | boolean | |
| `PrimitiveType` | string | nullable |
| `FormatRef` | FK→Formats | nullable |
| `EnumVersionRef` | FK→EnumVersions | nullable |
| `SubTypeVersionRef` | FK→TypeVersions | nullable |
| `HelperRef` | FK→TypeHelpers | nullable; supports nested helpers |
| `RawJson` | string | |

(Same shape as `TypeAttributes` minus the `oneOf` machinery — keeping it intentionally redundant rather than collapsing the two tables, because helpers are not versioned and this preserves clean parent FKs.)

---

## Day-1 Module 2: Version upgrades

### Why this is in Module 1, not Tier 2

The current upgrade chain lives entirely in Python under `src/sema/runtime/{types,enums}/old_versions/*.py` — 19 type-upgrade methods and an implicit enum-bump pattern. **It is the only part of the schema-of-record that lives in code, not data**, which means today it can't be edited from Airtable, an admin UI, or the rulebook itself.

Modeling upgrades alongside the type/enum schema closes that gap and makes the rulebook a complete editing surface. Per principle 4, the goal is **declarative for the universal cases, escape hatch for the rest** — not "force every case into a table."

### Upgrade-operation taxonomy (from surveying all 19 existing methods)

| Pattern | Existing examples | Status |
|---|---|---|
| Pure additive (new optional field, no transform) | `ha1_params 004→005` | declarative |
| Add field with constant default | `derived_channel_gt 000→001`, `layout_lite 007→008`, `i2c…002→003`, `ha1_params 005→006` | declarative |
| Remove field | `fsm_atomic_report 000→001` removes `ActionType` | declarative |
| Required → Optional / Optional → Required | `ha1_params 005→006` | declarative |
| Enum version bump (name-preserving) | `data_channel_gt 001→002` (`TelemetryName 006→007`) | declarative |
| Recursive subtype upgrade | `fsm_full_report 000→001`, `report_event 002→003` | declarative |
| Recursive list-element upgrade | `report 002→003`, `i2c…003→004` | declarative |
| Conditional recursive upgrade (only if version matches) | `layout_lite 009→010` | declarative |
| Mixed-version array consolidation | `layout_lite 011→012` | declarative |
| String → enum-value coercion | `spaceheat_node_gt 200→300` | declarative |
| Computed/projected field add | `data_channel_gt 001→002` (`SpaceheatTelemetryQuantityProjection.project(...)`) | declarative via `Projections` |
| Polymorphic restructure with conditional logic | `fsm_atomic_report 000→001` (flatten `(ActionType, Action)` into tagged union, raise on unsupported `ActionType`) | **escape hatch (`RawScript`)** |

**16 of 19 upgrade methods are pure-data declarative**, 1 needs a first-class projection concept, 2 need an escape hatch.

### Schema details — Module 2

#### `Projections`
Named, deterministic enum-to-enum (or value-to-value) mappings. Today's two cases are `SpaceheatTelemetryQuantityProjection` (TelemetryName → Quantity) and `Gw1UnitQuantityProjection` (Unit → Quantity).

| Column | Type | Notes |
|---|---|---|
| `Name` | string | PK; e.g. `SpaceheatTelemetryQuantityProjection` |
| `Description` | string | |
| `FromEnumVersion` | FK→EnumVersions | source domain |
| `ToEnumVersion` | FK→EnumVersions | target domain |
| `RawScript` | string | nullable; populated only if the projection isn't a flat lookup (escape hatch) |

#### `ProjectionMappings`
The actual value-by-value table when the projection *is* a flat lookup.

| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=Projection & ":" & FromSymbol` |
| `Projection` | FK→Projections | |
| `FromSymbol` | string | source enum symbol |
| `ToSymbol` | string | target enum symbol |
| `Description` | string | nullable |

#### `TypeUpgrades`
One row per ordered version pair `(N, N+1)` for a given type.

| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=FromTypeVersion & "→" & ToTypeVersion` |
| `FromTypeVersion` | FK→TypeVersions | |
| `ToTypeVersion` | FK→TypeVersions | |
| `Description` | string | the docstring summary |
| `RawScript` | string | nullable; whole-method escape hatch when no op decomposition is clean |

#### `TypeUpgradeOps`
One row per atomic operation within an upgrade. Most upgrades decompose into 1–4 ops.

| Column | Type | Notes |
|---|---|---|
| `Name` (calc) | string | `=TypeUpgrade & "#" & Idx` |
| `TypeUpgrade` | FK→TypeUpgrades | |
| `Idx` | integer | execution order |
| `OpKind` | enum | see vocabulary below |
| `FieldName` | string | nullable; the attribute touched |
| `LiteralValue` | string | nullable; JSON-encoded literal (for `AddWithDefault`) |
| `FromVersion` | string | nullable; source version for conditional upgrades |
| `ToVersion` | string | nullable; target version for explicit version bumps |
| `EnumVersionRef` | FK→EnumVersions | nullable; for enum-related ops |
| `ProjectionRef` | FK→Projections | nullable; for projected adds |
| `RawScript` | string | nullable; per-op escape hatch (preferred over whole-method `RawScript`) |
| `Description` | string | nullable |

#### `OpKind` vocabulary (12 values)

| Kind | Required cols | Semantics |
|---|---|---|
| `AddOptional` | `FieldName` | new optional field, no transform |
| `AddWithDefault` | `FieldName`, `LiteralValue` | new field with literal default |
| `Remove` | `FieldName` | drop field from payload |
| `RequireToOptional` | `FieldName` | relax requirement |
| `OptionalToRequire` | `FieldName` | tighten requirement (caller must guarantee field present) |
| `EnumVersionBump` | `FieldName`, `EnumVersionRef` | name-preserving enum upgrade |
| `CoerceToEnum` | `FieldName`, `EnumVersionRef` | coerce string value into versioned enum |
| `UpgradeChild` | `FieldName` | call `.upgrade()` on a versioned subtype field |
| `UpgradeChildIf` | `FieldName`, `FromVersion` | conditional `UpgradeChild` |
| `UpgradeListItems` | `FieldName` | `.upgrade()` per array element |
| `UpgradeListItemsIf` | `FieldName`, `FromVersion` | per-element conditional upgrade |
| `AddProjected` | `FieldName`, `ProjectionRef`, `LiteralValue` (source-field name) | populate via `Projections` row |
| `Custom` | `RawScript` | escape hatch — Python snippet runs in scope of `self` and `data` dict |

#### `EnumUpgrades` and `EnumUpgradeMappings`
Mirror of `TypeUpgrades` but for enum value renames or splits when name preservation breaks.

```
EnumUpgrades(FromEnumVersion→, ToEnumVersion→, Description, RawScript)
EnumUpgradeMappings(EnumUpgrade→, FromSymbol, ToSymbol, Description)
```

None of today's 5 multi-version enums needed value renames (all preserved names), so these tables start empty. They exist on day one because the moment any rename happens, the modeling needs to be there — promotion-after-the-fact would force a reshape of `TypeUpgradeOps.EnumVersionBump` semantics.

### Worked examples (showing this actually fits)

**Trivial — `ha1_params 004→005`** (5 optional adds):
```
TypeUpgrade: ha1.params/004 → ha1.params/005
  Op 1: AddOptional      FieldName=CopIntercept
  Op 2: AddOptional      FieldName=CopOatCoeff
  Op 3: AddOptional      FieldName=CopLwtCoeff
  Op 4: AddOptional      FieldName=CopMin
  Op 5: AddOptional      FieldName=CopMinOatF
```

**With projection — `data_channel_gt 001→002`**:
```
TypeUpgrade: data.channel.gt/001 → data.channel.gt/002
  Op 1: EnumVersionBump  FieldName=TelemetryName
                         EnumVersionRef=spaceheat.telemetry.name/007
  Op 2: AddProjected     FieldName=Quantity
                         ProjectionRef=SpaceheatTelemetryQuantityProjection
                         LiteralValue=TelemetryName        (source field)
```

**Recursive — `report 002→003`**:
```
TypeUpgrade: report/002 → report/003
  Op 1: UpgradeListItemsIf FieldName=FsmReportList
                           FromVersion=000
```

**Escape hatch — `fsm_atomic_report 000→001`** (the polymorphic restructure):
```
TypeUpgrade: fsm.atomic.report/000 → fsm.atomic.report/001
  Op 1: Remove          FieldName=ActionType
  Op 2: Custom          RawScript=<Python: validate ActionType=="RelayPinSet",
                                  build FsmAtomicReportSimpleAction(...)>
```

The escape-hatch op is a real Python snippet round-tripped from the existing `.upgrade()` method body. It's still data, it's still in the rulebook, it's still editable in the admin UI — it just isn't decomposed into atomic declarative ops.

### Self-check: did we just push everything into `RawScript`?

No. By the survey: 16 of 19 existing upgrades are fully declarative with the 12-op vocabulary above; 1 uses `AddProjected`; 2 require `Custom` ops for restructuring. That's an **89% declarative coverage** before we even start tuning the op vocabulary. Future upgrades that hit a new declarative pattern (e.g., field rename) get a new `OpKind` value added — additive change, no schema reshape.

---

## Migration tool design

Four tools total: two for the schema-of-record (Module 1), two for version upgrades (Module 2). Each pair has an importer (legacy → rulebook) and an emitter (rulebook → legacy artifact, run every build).

### Tool 1: `yaml-to-rulebook` (one-shot — establishes the rulebook)

Inputs:
- `definitions/owners.yaml`
- `definitions/registry.yaml`
- `definitions/formats/*.yaml`
- `definitions/enums/{name}/{NNN}.yaml`
- `definitions/types/{name}/{NNN}.yaml`

Output:
- `effortless-rulebook/effortless-rulebook.json` (replacing the 39-byte stub)

Algorithm:
1. Load `owners.yaml` → `Owners` rows.
2. Load `registry.yaml` → name-level rows for `Formats`, `Enums`, `Types`.
3. Walk `definitions/formats/*.yaml` → fill in `Formats` columns + `FormatExamples` rows.
4. Walk `definitions/enums/{name}/{NNN}.yaml` → emit `EnumVersions` rows + `EnumValues` rows (with `value_descriptions`).
5. Walk `definitions/types/{name}/{NNN}.yaml`:
   - emit `TypeVersions` row.
   - walk `properties` map → emit `TypeAttributes` rows; resolve `$ref` URLs into the appropriate FK column.
   - when `properties.X.items.type == 'object'` → synthesize `TypeHelper` (name: `<parent>.<X-singular-or-X-Item>`), emit helper + helper-attributes; set parent `TypeAttribute.HelperRef`.
   - when `properties.X.oneOf` is present → store the entire `oneOf` body verbatim in `TypeAttribute.RawJson`; emit a migration warning (`OneOfDeferredToRawJson`) so we can track when n>1 and revisit.
   - skip `TypeName`/`Version` consts (auto-emitted on round-trip).
   - flag `additionalProperties` → `TypeVersions.ExtraAllowed`.
   - emit `TypeExamples` rows from `examples`.
   - emit `TypeAxioms` rows from `x-gridworks.axioms`.
   - park unmodeled fields in `RawJson`.

Resolution rules:
- `$ref → /formats/X` → `FormatRef = X`.
- `$ref → /enums/X/NNN` → `EnumVersionRef = (X, NNN)`.
- `$ref → /types/X/NNN` → `SubTypeVersionRef = (X, NNN)`.

Helper-naming rule (deterministic, so round-trip is stable):
- For array items: `<ParentTypeName>.<AttrNameSingular>` where `AttrNameSingular = AttrName` with trailing `s` / `List` stripped (e.g., `RelayNodes` → `RelayNode`, `ChannelReadingsList` → `ChannelReading`). Falls back to `<AttrName>Item` if no singular form is detectable.
- For `oneOf` branches: `<ParentTypeName>.<AttrName>.Branch<N>` (1-indexed).

### Tool 2: `rulebook-to-yaml` (round-trip emitter — runs every build)

Inputs:
- `effortless-rulebook/effortless-rulebook.json`

Outputs:
- regenerated `definitions/` tree (overwriting current YAML files).

Algorithm:
1. For each `Owner` row → upsert `definitions/owners.yaml`.
2. Build top-level `definitions/registry.yaml` from `Formats` / `Enums` / `Types` rows + their version-level `Created`/`Status`/`Description` data.
3. For each `Format` row → emit `definitions/formats/{Name}.yaml`.
4. For each `EnumVersion` row → emit `definitions/enums/{Enum.Name}/{Version}.yaml`, including `value_descriptions` from child `EnumValues`.
5. For each `TypeVersion` row → emit `definitions/types/{Type.Name}/{Version}.yaml`:
   - synthesize `TypeName` and `Version` `const` properties.
   - walk `TypeAttributes` ordered by `Idx`:
     - if `HelperRef` set and parent `IsList` → emit `type: array` with inline `items: {…}` re-inlined from `TypeHelpers` + `TypeHelperAttributes` (using `OriginPath` to verify placement is correct).
     - if `RawJson` contains a `oneOf` body → emit it verbatim (round-trip via blob).
     - else → emit `$ref:` URL or primitive declaration.
   - emit `required:` from rows where `IsRequired=true`.
   - emit `additionalProperties:` from `ExtraAllowed`.
   - emit `examples:` from child `TypeExamples`.
   - emit `x-gridworks: { owner, axioms }` from `Owner` + `TypeAxioms`.

### Round-trip guarantee (Module 1)

The Module-1 tools must satisfy:

```
canonicalize(yaml) == canonicalize(rulebook-to-yaml(yaml-to-rulebook(yaml)))
```

where `canonicalize` strips comments, normalizes key ordering, and normalizes whitespace. Implemented as **golden tests**: every YAML file in `definitions/` is run through the round-trip and compared against itself.

Initial run is allowed to surface a small set of files that don't round-trip cleanly; those become known-issue tickets, not failures. Once all 118 files (69 types + 38 enums + 11 formats) round-trip, the rulebook becomes the source of truth.

### Tool 3: `python-upgrades-to-rulebook` (one-shot — extracts upgrade chain)

Inputs:
- `src/sema/runtime/types/old_versions/*.py`
- `src/sema/runtime/enums/old_versions/*.py`
- The two existing projection classes (`SpaceheatTelemetryQuantityProjection`, `Gw1UnitQuantityProjection`)

Output:
- New rows in `Projections`, `ProjectionMappings`, `TypeUpgrades`, `TypeUpgradeOps`, `EnumUpgrades`, `EnumUpgradeMappings`.

Algorithm:
1. AST-parse each old-version file, locate the `def upgrade(self) -> X:` method.
2. Pattern-match the method body against the 12-op vocabulary:
   - `data["X"] = <literal>; data["version"] = "Y"; return ...` → `AddWithDefault` op.
   - `data.pop("X", None)` → `Remove` op.
   - `data["X"] = self.X.upgrade()` → `UpgradeChild` op.
   - `data["X"] = [item.upgrade() for item in self.X]` → `UpgradeListItems` op.
   - `data["X"] = [item.upgrade() if item.version == "V" else item for item in self.X]` → `UpgradeListItemsIf` op.
   - `if self.X.version == "V": data["X"] = self.X.upgrade()` → `UpgradeChildIf` op.
   - Calls into a `*Projection.project(...)` helper → `AddProjected` op (with its source enum-version pair captured into `Projections`).
   - Anything not matching → emit a single `Custom` op with the verbatim method body (sans the boilerplate `data = self.model_dump()` / `data["version"] = "Y"` / `return X.model_validate(data)`).
3. Walk the docstring to extract `Description`.
4. For projection helpers: parse the class, emit a `Projections` row + `ProjectionMappings` rows for each `(from_symbol, to_symbol)` pair. If the projection logic isn't a flat lookup, populate `Projections.RawScript` instead.
5. Emit a coverage report: how many ops decomposed declaratively, how many fell back to `Custom`.

Acceptance bar: ≥80% of upgrade ops decompose declaratively without intervention. Manual edits welcome before commit (e.g., a method the AST parser couldn't classify might be one a human can split into 2 ops + 1 `Custom`).

### Tool 4: `rulebook-to-python-upgrades` (round-trip emitter — runs every build)

Inputs:
- `effortless-rulebook/effortless-rulebook.json` (the upgrade-chain tables).

Outputs:
- Regenerated `src/sema/runtime/types/old_versions/*.py` and `src/sema/runtime/enums/old_versions/*.py`.

Algorithm: each `TypeUpgrades` row → one Python class with `.upgrade()` method, body assembled by walking ordered `TypeUpgradeOps` and emitting per-op snippets from a small Jinja2 template per `OpKind`. `RawScript` ops paste verbatim. Imports computed from the FK targets. Black/Ruff post-format.

### Round-trip guarantee (Module 2)

```
old_versions/*.py
  └─► python-upgrades-to-rulebook
        └─► rulebook
              └─► rulebook-to-python-upgrades
                    └─► old_versions/*.py  (functionally equivalent)
```

The functional bar: for every existing test under `tests/runtime/`, the regenerated upgrade methods produce identical outputs given identical inputs. Byte-equivalence of the Python files is *not* required (Black/Ruff might normalize formatting), but behavioral equivalence is.

---

## Tier-2 expansion path

Everything below is **strictly additive** — new columns or new tables, no reshape of Tier-1 data.

### Per-attribute Tier-2 columns (column-add on `TypeAttributes`)

From ODXML — populated as the rulebook absorbs ODXML data:

- `DefaultValue`, `TestValue`, `Title`, `Url`
- `PreValidateFormat`, `UseEnumAlias`, `EnumLocalName`
- `ImmutableInDc`, `OnCreate`, `OnUpdate`
- `TypeInPayload`

### Per-type Tier-2 columns (column-add on `Types`)

- `ProtocolCategory`, `SendName`, `ReplaceWith`, `ReplaceWithTypeNameRoot`, `ConsistencyCheck`

### Per-format Tier-2 columns (column-add on `Formats`)

- `DefaultFail1`, `PreValidateFormat`, `FromEnum`

### New axiom column

- `TypeAxioms.CheckFirst`, `TypeAxioms.OnCreate`, `TypeAxioms.OnUpdate`, `TypeAxioms.SinglePropertyAxiom`, `TypeAxioms.MultiPropertyAxiom`, `TypeAxioms.Title`, `TypeAxioms.Description`

### New tables (additive new dimensions)

- **Protocol grouping:** `Protocols`, `ProtocolTypes`, `ProtocolEnums`
- **REST routing:** `RestfulGets`, `RestfulPosts`
- **Rabbit routing:** `Topics`, `RabbitExchangeRoles`, `RabbitPairings`
- **GNode taxonomy:** `GNodeRoles`
- **Permissions:** per-row `UserCRUD`, `GuestCRUD`, `AdminCRUD` columns on every entity
- **Ontology grouping:** `OntologyGroups` + FK column on each entity
- **Discriminator-keyed `oneOf`:** `TypeAttributes.DiscriminatorField` column (one column add)

### `oneOf` promotion (when n>1)

Once a second `oneOf` use case appears in the YAML, promote from blob to first-class:

- Add `TypeAttributes.IsOneOf` boolean column.
- Add new `TypeAttributeBranches` table: `TypeAttribute→`, `Idx`, `HelperRef→TypeHelpers`, `Description`.
- If discrimination is structural across all known cases, that's the final shape.
- If any case uses an explicit discriminator key (`kind:` / `type:`), add `TypeAttributes.DiscriminatorField` at that point.
- One-shot script reads `RawJson.oneOf` for affected rows, synthesizes `TypeHelpers` + `TypeAttributeBranches`, clears the blob.
- All additions are pure column/table adds; existing rulebooks remain readable.

---

## Phasing

### Phase 0 — Schema lock

- Review and approve this plan.
- Convert the table specs above into a populated `effortless-rulebook.json` skeleton (just `schema[]` arrays, empty `data[]`).
- Run `effortless build` to confirm postgres + views generate correctly off the empty rulebook.

### Phase 1 — `yaml-to-rulebook` migrator

- Implement the algorithm above.
- Run against all 118 YAML files.
- Inspect output, fix migration bugs.
- Commit the populated rulebook to git as the first real snapshot.

### Phase 1.5 — Upgrade-chain extraction (`python-upgrades-to-rulebook`)

- Implement the AST-pattern-matching importer for old-version `.upgrade()` methods.
- Run against all 19 type-upgrade methods + projection helpers.
- Manually triage the coverage report: any method that fell back to `Custom` gets a human pass — split into declarative ops where possible, accept `Custom` where genuinely procedural.
- Extend rulebook with populated `Projections`, `TypeUpgrades`, `TypeUpgradeOps`, etc.
- This phase can run in parallel with Phase 2 (Module 1 emitter) since they touch disjoint tables.

### Phase 2 — Round-trip emitters + golden tests

- Implement `rulebook-to-yaml` emitter (Module 1).
- Implement `rulebook-to-python-upgrades` emitter (Module 2).
- Add golden tests: YAML files round-trip canonical-equivalent; old-version Python upgrade methods round-trip behaviorally-equivalent (verified against existing `tests/runtime/`).
- Iterate until clean.

- Implement the emitter.
- Add golden test that round-trips every YAML file and asserts canonical equivalence.
- Iterate until clean.

### Phase 3 — Cutover

- Make the rulebook the canonical source. Both the YAML directory *and* the `old_versions/*.py` files become generated output (still committed, but with a `# GENERATED — DO NOT EDIT` header).
- Move the `build_*.py` index builders to read from the rulebook (or from `vw_*` postgres views if the build is in place).
- Add a CI check that runs both emitters and fails if uncommitted YAML or Python drift is detected.

### Phase 4 — Admin UI

- Stand up an ERB-driven admin UI (postgres + standard ERB scaffolding) for editing types, enums, formats, axioms, helpers, **and version upgrades** (a `TypeUpgrades` editor with per-op rows, plus a `RawScript` text area for `Custom` ops).
- Editing happens against postgres; on commit, export a fresh rulebook JSON and regenerate YAML + old-version Python.

### Phase 5 — Tier-2 expansion (interleaved with Phase 4 onward)

- Absorb ODXML's protocol/REST/Rabbit/GNode/CRUD dimensions into the rulebook one table or one column at a time, populated from `Airtable.xml`.
- Each absorbed dimension lets one XSLT step retire (its data now comes from rulebook views).

### Phase 6 — Decommission Set A

- Once every concept ODXML carries is in the rulebook, delete `code_gen/GridworksCore/aicapture.json` transpiler entries one by one.
- Delete the legacy 3.7 MB `code_gen/GridworksCore/effortless-rulebook.json` stub.
- Optionally: re-target the `AirtableTo*` transpilers at the rulebook so Airtable becomes a downstream view of the rulebook (round-trip with Airtable as editor).

---

## Open items deferred for later decision

- **Postgres permissioning.** ERB convention for admin-UI vs. service access — punt to Phase 4.
- **Magic-links auth on the admin UI.** If the admin UI is multi-tenant, layer in via the `magic-links` skill.
- **Index builder source.** Decide whether `build_dependency_closure.py` etc. read from rulebook JSON, postgres views, or YAML — likely views, but lock in at Phase 3.
- **Status field semantics.** `EnumVersions.Status` and `TypeVersions.Status` accept any string today; tighten to an enum (`active`, `deprecated`, `draft`, …) in Tier 2 once values are surveyed.
- **Naming policy for synthesized helpers.** The `RelayNodes → RelayNode` rule is a heuristic. Edge cases (e.g., `MachineStates` → `MachineState`, but `Status` → `Status`) may need a manual override map.
- **JSON-Schema features not yet handled.** `if/then/else`, `allOf`, `not`, `patternProperties`, `dependentRequired` — currently land in `RawJson`. If any appear in future YAML, decide per-feature whether to flat-model.
- **`OpKind` vocabulary growth.** New declarative patterns (e.g., `RenameField`, `SplitField`, `MergeFields`) get added as new `OpKind` enum values when a real case appears. Each addition is a column-add on the enum, never a schema reshape.
- **Downgrade chain.** Today there's no `.downgrade()`; if needed later, `TypeUpgradeOps` can either grow a `Reversible` flag with auto-inverted ops, or we add a parallel `TypeDowngradeOps`. Defer until requested.
- **Cross-version test fixtures.** Existing `tests/runtime/` exercises the upgrade chain against real payloads. Phase 2 must keep those passing as the regenerator's correctness bar — but whether *new* fixtures should be model-driven (rulebook rows describing expected upgrade results) is its own design question.

---

## What we are explicitly not doing

- **Not** maintaining ODXML and rulebook in parallel long-term. ODXML is decommissioned at Phase 6.
- **Not** modeling JSON-Schema down to ground truth. `RawJson` is the agreed escape hatch for the long tail.
- **Not** introducing a "rulebook version" record inside the rulebook. The file is the snapshot; git is the version history.
- **Not** modeling Airtable record IDs or any Airtable-specific metadata in the rulebook. Airtable becomes one downstream consumer like any other.
- **Not** over-fitting `oneOf` to the single current example. The single existing case round-trips via `RawJson` blob until n>1, at which point we promote to a first-class `TypeAttributeBranches` table — a pure additive change (new column, new table). This is a deliberate flexibility-over-modeling choice.
- **Not** forcing every upgrade method into declarative ops. `TypeUpgradeOps.RawScript` (per-op) and `TypeUpgrades.RawScript` (whole-method) escape hatches preserve lossless round-trip without sacrificing correctness on the 2 of 19 cases that legitimately need procedural logic.
