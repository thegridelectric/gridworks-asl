# ERB Scaffold Plan — Expressing HEAD from the Rulebook

**Status:** Active. Supersedes the relevant sections of [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) and [JM_DERIVED_INTEGRATION_PLAN.md](JM_DERIVED_INTEGRATION_PLAN.md), which remain useful for context but are pre-`jm/derived`.

**Window of reference:** the changes summarized in [CLI_CHANGE_REPORT.md](CLI_CHANGE_REPORT.md).

---

## 0. Goal

Build an **ERB scaffold around all of legacy HEAD** — YAML SSoT, CLI surface, runtime generation pipeline, vocabulary catalog, emitter inventory, lifecycle governance — so that every observable feature in HEAD is **describable** (not necessarily *implemented*) from `effortless-rulebook/effortless-rulebook.json`.

This is the **SDLAF / CMCC** stance: per-fact / per-inference rows in a DAG, not "complex runtime joins." Each capability gets a row (or a small group of rows); each derived view gets a calculated field; nothing lives in opaque Python that the rulebook can't *point at*.

**What "fully expressible" means here:**

- Every CLI verb / subcommand / flag is a row.
- Every YAML file under [definitions/](definitions/) is reachable from a rulebook row whose calculated field knows the file path.
- Every emitter / transpiler under [rulebook-emitters/](rulebook-emitters/) is a row with its inputs, outputs, and language target.
- Every template under [src/sema/tools/runtime_generation/templates/](src/sema/tools/runtime_generation/templates/) is a row linked to the Type/Enum version it implements.
- Every snapshot, seed request, public-registry entry, lifecycle state, and index file the pipeline produces is modeled.
- Implementations stay in Python *for now* — the rulebook just **scaffolds** them. Later work (the "make HEAD generated from ERB" goal) layers on top.

---

## 1. Frame: what HEAD looks like today

(From the explore pass + [CLI_CHANGE_REPORT.md](CLI_CHANGE_REPORT.md).)

### 1.1 YAML SSoT — [definitions/](definitions/)
- `types/` — ~102 YAML files, ~69 types × ~1.5 versions avg.
- `enums/` — ~47 files, ~32 enum names, some multi-version.
- `formats/` — ~14 files (regex / bounds validators).
- `registry.yaml` — metadata (owner, schema_url, created, description).
- `owners.yaml` — owner records.

### 1.2 CLI — [src/sema/interfaces/cli/](src/sema/interfaces/cli/)
| File | Verb / subcommand | Purpose |
|------|-------------------|---------|
| `main.py` | `sema info` | Display CLI surface. |
| `snapshot.py` | `sema snapshot prepare <seed.yaml>` | Restrict + expand closure → `output/sema/indexes/`. |
|  | `sema snapshot build --package-name X` | Generate Python SDK from prepared snapshot. |
| `runtime.py` | `sema runtime scaffold-axiom-template <type> <ver>` | Create missing axiom jinja stub. |
|  | `sema runtime scaffold-upgrade-template <type> <ver> <next>` | Create missing upgrade jinja stub. |
| `reverse.py` | `sema reverse <name> [version]` | Show transitive reverse dependencies. |

### 1.3 Tooling — [src/sema/tools/](src/sema/tools/)
- Index builders: `build_public_registry`, `build_dependency_closure`, `build_reverse_dependencies`, `build_lookup`, `build_versions`.
- Snapshot helpers: `build_seed_dag`, `build_seed_definitions`, `build_seed_expanded`, `seed_requests` (pydantic models).
- Upgrade extraction (not yet wired): `python_upgrades_to_rulebook`.

### 1.4 Emitters — [rulebook-emitters/](rulebook-emitters/)
- `yaml/` — YAML↔Rulebook round-trip (~96.6% pass).
- `python/` — Rulebook→Python (scaffolded, not wired into build).
- `golang/` — Rulebook→Go (scaffolded only).
- `html/` — empty placeholder.
- `shared/` — common utilities.

### 1.5 Runtime templates — [src/sema/tools/runtime_generation/templates/](src/sema/tools/runtime_generation/templates/)
- `axioms/*.py.jinja2` — ~7+ axiom implementations.
- `upgrades/*.py.jinja2` — ~17+ upgrade implementations.
- Generation **fails** if a schema declares an axiom/upgrade without a template (per [87bbeef](commit)).

### 1.6 Existing rulebook tables (20)
- **Schema-of-record (13):** Owners, Formats, FormatExamples, Enums, EnumVersions, EnumValues, Types, TypeVersions, TypeAttributes, TypeExamples, TypeAxioms, TypeHelpers, TypeHelperAttributes.
- **Upgrade chain (6):** Projections, ProjectionMappings, TypeUpgrades, TypeUpgradeOps, EnumUpgrades, EnumUpgradeMappings.
- **App (1):** AppUsers.

---

## 2. What is *missing* from the ERB

Below is the full punch-list. Each entry: **WHY it's missing**, **WHAT to add** (tables / fields), **HOW the loop verifies it**. Order is intentional — earlier items unblock later items.

### Tier A — Pipeline-shape (post-`jm/derived` work that the old plan predates)

#### A1. Lifecycle / governance fields on existing tables — **DONE (effectively no-op)**

**Status correction (2026-05-15):** the original A1 wording was based on a hallucinated lifecycle vocabulary. The only Status values in sema are `draft` and `published`, and they exist exclusively at the *version* level (TypeVersions / EnumVersions). The concepts `active`, `deprecated`, `retired`, `IsActive`, `IsDeprecated`, `IsRetired`, `RetiredAt`, and a parent-level `Status` field were all hallucinations and have been removed from this plan. Parent-table liveness is derived from versions via the existing aggregations (`HasDrafts`, `PublishedVersionCount`, `DraftVersionCount`).

**What was actually missing:** nothing. `Types.ReplacedBy`, `Enums.ReplacedBy`, `Formats.ReplacedBy` were already in the rulebook before this tier was started. The per-version `Status` field (`draft | published`) was already present on TypeVersions and EnumVersions.

**Cleanup performed in this tier instead:**
- Removed 26 orphan calc-function bodies from [postgres/02b-customize-functions.sql](postgres/02b-customize-functions.sql) that referenced the hallucinated vocabulary (`calc_*_is_active`, `calc_*_is_deprecated`, `calc_*_is_retired`, `calc_*_word_is_retired`, `ref_is_stale`, plus the active/deprecated/retired `*_count` rollups).
- Activated the DROP-views-and-functions block in [postgres/00-bootstrap.sql](postgres/00-bootstrap.sql) so every `effortless build` runs against a clean slate of derived objects. Tables and their data are never dropped here — schema evolution stays additive via `ALTER TABLE ADD COLUMN IF NOT EXISTS`.

**Lesson:** future tiers that talk about lifecycle MUST use only `draft | published`. See memory `feedback-lifecycle-vocab` and `plan-doc-caveat`.

#### A2. PublicRegistry — **SUBSUMED, NO WORK NEEDED**

**Status correction (2026-05-15):** A2 as originally drafted (and as I tried to rewrite in 227a587) was another instance of the same mistake §A1 corrected. There is no "is in the public registry" state separate from "has been published" — they are the same fact. The public registry of types/enums is literally the set of rows where `PublishedVersionCount > 0`; the public registry of formats is the set of formats. Both are filters over existing data, not new state to model.

These are *immutable versioned protocols*: a version has been published or it hasn't. Once published it's permanent. Adding `IsInPublicRegistry`, `PublicRegistryEntry`, or any sibling field is categorically wrong — equivalent to putting an "IsActive" flag on the HTTP protocol.

**The "public registry" expressed in current ERB terms (no new fields):**
- Public types: `SELECT * FROM vw_types WHERE published_version_count > 0`
- Public enums: `SELECT * FROM vw_enums WHERE published_version_count > 0`
- Public formats: `SELECT * FROM vw_formats` (Formats have no version axis; all rows are public)

The JSON shape that `build_public_registry.py` emits is constructible directly from these views — no rulebook field needs to wrap it. If a future Tier wants to model the *index file itself* as a row (a `public_registry` row in the `IndexBuilders` catalog from §A4), that's where the registry's existence is recorded, not on Types/Enums/Formats.

**Verify:** none required — there's nothing to build.

#### A3. SeedRequests + Snapshots
**Why:** the `snapshot prepare`/`build` pair takes a seed YAML, produces `output/sema/` with restricted definitions + indexes + `local_names.yaml`, and runs runtime generation. None of this is in the ERB.

**Changes (new tables):**
- `SeedRequests` — Name, PackageName, Description, RootTypes (FK[], multi → Types), IncludeAllVersions (bool), Owner.
- `SeedRequestEntries` — SeedRequest, Type/Enum/Format selector, VersionSelector, Reason. (The granular form, if needed beyond root types.)
- `Snapshots` — Name, SeedRequest (FK), BuiltAt, OutputPath, PackageImportRoot, Status (prepared | built | published), CommitSha (text).
- `LocalNames` — Snapshot (FK), CanonicalName, LocalName, Kind (type|enum|format). Models `local_names.yaml`.

**Verify:** `vw_seed_requests`, `vw_snapshots`, `vw_local_names`. Cross-reference one real seed YAML against its rulebook row.

#### A4. IndexBuilders catalog
**Why:** what actually exists in HEAD is a set of **builder scripts**, not the index files themselves. [scripts/build_indexes.sh](scripts/build_indexes.sh) runs five Python builders in a fixed order (with `build_public_registry` intentionally re-run last). The ERB should model the **builders** as first-class rows — their ordering, their script path, their inputs/outputs — because *that's* what HEAD will need to be regenerated from the rulebook later. The output files (`indexes/*.yaml`) are downstream artifacts, not catalog entries.

**Changes (new table):**
- `IndexBuilders` — Name, ScriptPath (e.g. `src/sema/tools/build_public_registry.py`), RunOrder (int — the position in `build_indexes.sh`), InputsDescription, OutputPath (e.g. `indexes/public_registry.yaml`), DependsOn (FK[] → IndexBuilders), Description, RerunAfter (FK → IndexBuilders, nullable — captures the `build_public_registry` re-run at the end).
- Calculated: `IndexBuilders.IsTerminal` (TRUE if no other builder lists it as DependsOn).

**Seed rows:** the 6 invocations from [scripts/build_indexes.sh](scripts/build_indexes.sh) (5 distinct builders, with `build_public_registry` referenced twice via RunOrder — or once as a row with a `RerunAfter` self-pointer; pick whichever models cleaner).

**Verify:** `vw_index_builders`; ordering matches the shell script; `DependentCount` rollup sane.

**Note:** if we later want to model the orchestration scripts themselves (`build_indexes.sh`, `init-db.sh`, `start.sh`), that's a separate `OrchestrationScripts` table — flagged here, deferred until after Tier E.

#### A5. Templates registry
**Why:** axiom/upgrade templates are now required artifacts and live in [runtime_generation/templates/](src/sema/tools/runtime_generation/templates/). Their existence and binding to a TypeVersion/EnumVersion is what gates the build.

**Changes:**
- `Templates` — Name, Kind (axiom | upgrade | format | enum-runtime), Path (file path), Language (python, …), Status, OwnerVersion (polymorphic FK helper — see notes).
- `Templates.AxiomTypeVersion` (FK → TypeVersions, nullable)
- `Templates.UpgradeFromTypeVersion` (FK → TypeVersions, nullable)
- `Templates.UpgradeToTypeVersion` (FK → TypeVersions, nullable)
- `Templates.UpgradeFromEnumVersion`, `Templates.UpgradeToEnumVersion` (nullable).
- Calculated: `Templates.IsAxiom`, `Templates.IsUpgrade`, derived from which FKs are set (ERB doesn't allow polymorphic FK rows — use nullable concrete FKs and a discriminator).
- On `TypeVersions`: `HasAxiomTemplate` (rollup), `HasUpgradeTemplate` (rollup) → drives a "build will fail" warning view.

**Verify:** `vw_templates`; `vw_type_versions` shows correct rollups for the few axioms we already have implemented.

### Tier B — CLI scaffold

#### B1. CliCommands + CliFlags + CliExamples
**Why:** the user wants every CLI parameter / capability described in the ERB so tools can later regenerate the CLI plumbing.

**Changes (new tables):**
- `CliCommands` — Name (e.g. `sema snapshot prepare`), Parent (FK → CliCommands, nullable, for subcommands), ImplFile (text, e.g. `src/sema/interfaces/cli/snapshot.py`), Summary, IsLeaf (calc).
- `CliFlags` — Command (FK → CliCommands), Name (e.g. `--package-name`), ShortName, Kind (string|bool|int|path|enum), Required (bool), Default, Description, EnumValuesRef (FK → Enums, nullable — when the flag accepts an enum value).
- `CliExamples` — Command (FK), ExampleString, Description, ExpectedExitCode.

**Seed rows:** every command in §1.2 plus its flags.

**Verify:** `vw_cli_commands`, `vw_cli_flags`. Rollup `vw_cli_commands.FlagCount` matches the actual flags wired in Python.

### Tier C — Vocabulary pointers (YAML SSoT addressability)

#### C1. YamlFiles — pointer table
**Why:** the user explicitly asked for "pointers to the yaml files that formally define them." The ERB has Types/Enums/Formats but no row that says *this YAML file at this path defines version 003 of type X*.

**Changes:**
- `YamlFiles` — Path (text), Kind (type|enum|format|registry|owner), TypeVersion (FK, nullable), EnumVersion (FK, nullable), Format (FK, nullable), Sha (text, optional), IsGenerated (bool — false today, true post-Phase-3 cutover).
- Calculated on TypeVersions / EnumVersions / Formats: `YamlFilePath` = lookup into YamlFiles.

**Verify:** `vw_yaml_files` row-count ≈ filesystem count under `definitions/types/`, `enums/`, `formats/`. One canonical example per Tier.

### Tier D — Emitter / transpiler catalog

#### D1. Emitters
**Why:** [rulebook-emitters/](rulebook-emitters/) is the consumer side of the rulebook. We should be able to ask the rulebook "what languages can I emit to, what's the entrypoint, what's the status?"

**Changes:**
- `Emitters` — Name (yaml|python|golang|html), Path, Language, Status (working | scaffold | empty), InputKind (rulebook|snapshot), OutputKind (text), RoundTripPercent (calc/manual).

**Verify:** `vw_emitters`; rows match the directories under [rulebook-emitters/](rulebook-emitters/).

### Tier E — Features (the "what does HEAD do" surface)

#### E1. Features
**Why:** user explicitly called out "features." A Feature is a coarse capability ("snapshot build", "axiom-template enforcement", "round-trip YAML", "reverse-dependency listing") that may be implemented by 1..N CliCommands, Emitters, Templates, and Indexes. It's the human-readable index into everything else.

**Changes:**
- `Features` — Name, Summary, Status (planned | active | shipped), Owner, IntroducedInCommit (text, optional).
- `FeatureBindings` — Feature (FK), Kind (cli|emitter|index|template|table), TargetName (text — the row name in the bound table), Notes.
- Calculated on Features: `CliCommandCount`, `TemplateCount`, etc.

**Seed rows:** at minimum one Feature per major capability listed in §1 — snapshot pipeline, public-registry governance, axiom enforcement, upgrade enforcement, reverse-deps, round-trip yaml, AppUsers/magic-links, postgres codegen.

**Verify:** `vw_features` lists everything; counts reconcile with the bindings.

### Tier F — Optional / nice-to-have

#### F1. GitCommits (user said "maybe")
**Why:** lets the rulebook reference provenance — e.g., "this Template was introduced in commit X."

**Changes (small, optional):**
- `GitCommits` — Sha (text, PK-equivalent), Subject, Author, AuthoredAt, Branch.
- Allow nullable `IntroducedInCommit` text fields on Features / Templates / TypeVersions to *point at* a sha — but **don't** make it an FK unless we commit to keeping the GitCommits table populated by a build hook.

Skip for now if it adds friction. Re-evaluate after Tier A–E land.

#### F2. PipelineRuns (build telemetry)
**Why:** record each `effortless build` for diagnostics. Optional.

- `PipelineRuns` — StartedAt, FinishedAt, Status, CommitSha, GeneratedFiles (rollup count).

Treat as Phase-2 once the scaffold is meaningful.

---

## 3. The loop

This is the cadence the user asked for. Each turn of the loop is **one tier's worth or one row-group's worth** — small enough that a failed build is recoverable, large enough that the commit tells a story.

```
┌─ pick next missing ERB feature (start at Tier A1, work down) ───────────┐
│                                                                          │
│  1. design the rulebook delta                                            │
│     - new tables? new columns? new calculated fields?                    │
│     - which existing tables get FKs?                                     │
│                                                                          │
│  2. edit effortless-rulebook/effortless-rulebook.json                    │
│     - hand-edit; sema has no Airtable                                    │
│     - follow ERB conventions (PascalCase tables, no many-to-many,        │
│       Name field on every table, etc.)                                   │
│                                                                          │
│  3. run `effortless build`                                               │
│     - working tree must be clean before this; ask user if not            │
│     - this regenerates postgres/0[0-5]*.sql and drops/inits the DB       │
│                                                                          │
│  4. confirm every vw_* view loads                                        │
│     - psql -d sema -c "\dv vw_*"                                         │
│     - for f in $(psql -At -c "select viewname from pg_views             │
│       where schemaname='public' and viewname like 'vw\\_%'"); do         │
│       psql -d sema -c "select count(*) from $f" >/dev/null; done         │
│                                                                          │
│  5. commit the regenerated output BEFORE any hand edit                   │
│     - one commit: "effortless build: <tier/row-group>"                   │
│     - keeps generated and hand-written history separable                 │
│                                                                          │
│  6. review                                                               │
│     - did the new columns/fields capture what HEAD actually does?        │
│     - improve in next loop, or                                           │
│     - pick the next most-relevant unintegrated HEAD section              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Stop condition:** every capability listed in §2 has at least one row in its corresponding table, and `vw_features` cross-references every Tier-A–E entry. At that point the ERB *describes* HEAD; the next project (a separate week's work) is making HEAD *generated from* the ERB.

---

## 4. Bones inherited from the legacy plan

Worth preserving from [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md):

- The 13-table schema-of-record for types/enums/formats — **kept**, this scaffold only *adds* on top.
- The 6-table upgrade-chain — **kept** as-is.
- Escape hatches `RawJson` / `RawScript` for upgrade ops — **kept**; useful for axiom/upgrade template metadata that doesn't fit neat columns.
- The 12-op upgrade vocabulary — **kept**; remains the canonical alphabet for `TypeUpgradeOps`.
- Round-trip-as-validation philosophy — **kept**; the loop's step 4 is its modern form (verify via `vw_*` rather than via YAML diff).

What is **dropped** from the legacy plan (because HEAD moved past it):

- The "seed" CLI flow — replaced by `snapshot prepare` / `snapshot build`.
- The Phase-1.5 `python-upgrades-to-rulebook` migrator as written — supplanted by the template-driven model; the *extraction goal* survives but its target is now `Templates` rows + the upgrade tables.
- Phase-4 admin UI assumptions — the Explorer app moved into a separate scope (see [APP_PLAN.md](APP_PLAN.md)).

What is **kept** from [JM_DERIVED_INTEGRATION_PLAN.md](JM_DERIVED_INTEGRATION_PLAN.md):

- The principle that the rulebook is the **catalog**, jm's snapshot CLI is the **engine**.
- The round-trip parity goal (rulebook-emitters/yaml).
- The contract context (GridWorks SOW §3.1–§3.6) — unchanged.

---

## 5. Out of scope for this plan

- Reverse-generating Python from the ERB (later, once the scaffold is complete).
- Killing the YAML SSoT (Phase-3 cutover from the legacy plan — still real, still later).
- Killing `code_gen/GridworksCore/` (legacy ODXML — Phase 6, untouched).
- Airtable integration (sema has none and is not adding one).

---

## 6. Starting point for the next session

Pick Tier A1 (lifecycle fields). Smallest delta, exercises the loop, and unblocks A2 (PublicRegistry view) immediately. Then A3 → A4 → A5 → B → C → D → E in order. Tier F only after the scaffold is otherwise complete.
