# Registry Explorer — Navigation Plan

> **Scope.** This plan defines the navigation architecture, UX guiding principles, and implementation roadmap for an `/app/` version of the sema Registry Explorer — an admin-developer tool for seeing, editing, managing, navigating, exploring, documenting, and expanding the entire sema model. Treat it as the spine that everything else hangs off of.
>
> **Audience for now.** Administrative-level developers who need full-surface access to the registry. Future role-tailoring is discussed in §7, but the v1 surface is unified.
>
> **Stack (locked).** **React + TypeScript** on the front end; **FastAPI (Python)** on the back end. The API is intentionally thin — most computation already lives in postgres `vw_*` views and in the Python tooling under [rulebook-emitters/](rulebook-emitters/) and [src/sema/](src/sema/). FastAPI reads `vw_*` for live data, writes to base tables, and reuses [rulebook-emitters/shared/loader.py](rulebook-emitters/shared/loader.py) for any direct rulebook-JSON reads (e.g. schema introspection). Pydantic models from [rulebook-emitters/python/](rulebook-emitters/python/) become FastAPI response models when that emitter graduates from scaffold.
>
> **Status.** Draft, third pass — adds detailed roadmap (§12) and locks the stack. Grounded in the actual rulebook at [effortless-rulebook/effortless-rulebook.json](effortless-rulebook/effortless-rulebook.json) and the emitter scaffolding under [rulebook-emitters/](rulebook-emitters/).

---

## 0. What's actually in the rulebook today (snapshot)

So later sections aren't asserting things the rulebook can't back up:

**Tables (23):** `Owners`, `Types`, `TypeVersions`, `TypeAttributes`, `TypeAxioms`, `TypeExamples`, `Enums`, `EnumVersions`, `EnumValues`, `Formats`, `FormatExamples`, `Projections`, `ProjectionMappings`, `TypeUpgrades`, `TypeUpgradeOps`, `EnumUpgrades`, `EnumUpgradeMappings`, `TypeHelpers`, `TypeHelperAttributes`.

**Counts as of this writing:** 6 Owners, 46 Types, 68 TypeVersions, 570 TypeAttributes, 32 Enums, 38 EnumVersions, 11 Formats, 2 Projections, 20 TypeUpgrades, 4 TypeHelpers.

**The three lifecycle/retirement mechanisms in play, which are *not* the same:**

1. **Word-level retirement** — `Types.ReplacedBy`, `Enums.ReplacedBy`, `Formats.ReplacedBy`. Whole word retired in favor of a successor. Drives `Types.IsRetired` / `Enums.IsRetired` / `Formats.IsRetired` calc fields. The rulebook's own field description says: *"Words are immutable and may only be retired at the registry level (not per-version, per-value, or per-attribute)."*
2. **Definition-level lifecycle** — `TypeVersions.Status` and `EnumVersions.Status` (raw nullable strings). Drive `IsActive` (`Status="active"`) and `IsDeprecated` (`Status="deprecated"`) calc fields. **Currently null on all 68 TypeVersions and all 38 EnumVersions** — see §3.
3. **Closed/open shape** — `TypeVersions.ExtraAllowed` / `TypeHelpers.ExtraAllowed` flip the `IsClosed` calc (JSON-Schema `additionalProperties: false`). Orthogonal to lifecycle.

**Versioning surface, in three flavors** — important because the "fork" pattern (§9) splits along these:

| Surface | Has version chain? | Retirement mechanism | Tables |
|---|---|---|---|
| Types | Yes (`TypeVersions`) | `Types.ReplacedBy` for the whole Word | `Types`, `TypeVersions`, `TypeAttributes`, `TypeAxioms`, `TypeExamples` |
| Enums | Yes (`EnumVersions`) | `Enums.ReplacedBy` for the whole Word | `Enums`, `EnumVersions`, `EnumValues` |
| Formats | **No version chain** | `Formats.ReplacedBy` only | `Formats`, `FormatExamples` |
| Projections | **No version chain** | None — just unique `(FromEnumVersion, ToEnumVersion)` pairs | `Projections`, `ProjectionMappings` |
| TypeHelpers | **No version chain — scoped to a TypeVersion** | None — they travel with their `OriginTypeVersion` | `TypeHelpers`, `TypeHelperAttributes` |

**Migration surface:** `TypeUpgrades` + `TypeUpgradeOps` between two `TypeVersions`; **also** `EnumUpgrades` + `EnumUpgradeMappings` between two `EnumVersions`. The plan covers both.

---

## 0.5. The emitter infrastructure the Explorer leverages

The Explorer doesn't get built on a green field — there's existing scaffolding under [rulebook-emitters/](rulebook-emitters/) that the API and Phase 1 work both lean on.

**What exists today:**

| Path | Role | Status |
|---|---|---|
| [rulebook-emitters/shared/loader.py](rulebook-emitters/shared/loader.py) | Canonical accessors for the rulebook JSON: `load_rulebook`, `by_table`, `schema_for`, `index_by`, `group_by`, `table_summary`. Single point of failure if table shape changes. | Working |
| [rulebook-emitters/python/](rulebook-emitters/python/) | Will emit Pydantic classes for Types, IntEnum/StrEnum for Enums, format validators. | Scaffold (`out/TODO.txt`) |
| [rulebook-emitters/golang/](rulebook-emitters/golang/) | Will emit Go structs and typed enum constants. | Scaffold |
| [rulebook-emitters/html/](rulebook-emitters/html/) | Single-page documentation of the entire platform. | Scaffold (`out/sema.html` exists but minimal) |

**What the Explorer reuses:**

- **`shared/loader.py` from FastAPI** — for any read where the JSON is the right source of truth (e.g. `_meta`, raw schema introspection that doesn't hit `vw_*` views). The API process imports it directly; no copy-paste.
- **The python emitter's output (when it graduates)** — its emitted Pydantic classes become FastAPI's response models for `TypeVersions`, `EnumVersions`, etc. Until then, FastAPI hand-rolls thin Pydantic models that mirror the `vw_*` view columns. Swap-in is mechanical.
- **The HTML emitter is the read-only ancestor of the Explorer** — anything it can render (a static doc site of the registry) the Explorer must also render, just interactively. If a question like "where do TypeHelpers live in the docs?" has an answer in `html/`, the Explorer's Read mode owes the same answer.

**What the Explorer does NOT touch:**

- The emitters themselves — they're independent CLIs invoked manually. The Explorer is a separate process with a separate purpose (live editing vs. static codegen).
- [code_gen/GridworksCore/](code_gen/GridworksCore/) — slated for decommission, not consumed.
- The YAML round-trip tools at [rulebook-emitters/yaml/](rulebook-emitters/yaml/) — they're a pre-existing pipeline; the Explorer leaves them alone.

**Implication for the roadmap:** Phase 2's "data layer" task is not greenfield. It's a thin FastAPI app that imports `shared.loader`, queries postgres, and serves both. Phase 5's edit forms can crib their field-list shapes from the python emitter's planned output — when the python emitter implements real emission, the Explorer's response models become a `from rulebook_emitters.python.out import …` away.

---

## 1. The mental model (and what to call things)

Before navigation, we need names. The rulebook's nouns are technical (`Owners`, `Types`, `TypeVersions`...). The Explorer should let users think in editorial terms. Note: every Owner publishes more than just Words — the editorial vocabulary covers the **full Owner-published surface**.

| Editorial term | Rulebook entity | What it is |
|---|---|---|
| **Vocabulary** | `Owners` row | A namespace authored by one org/person (`gridworks-energy`, `microerapower`, …). An Owner can publish Words, Enums, **and** Formats. |
| **Word** | `Types` row | An immutable name (`bid`, `channel.config`, `report`). Per the rulebook: *"Words are immutable and may only be retired at the registry level."* Retired by setting `ReplacedBy`. |
| **Definition** | `TypeVersions` row | A frozen snapshot of what that Word meant at version `NNN` (`bid/000`, `bid/001`…). The unit of forking. |
| **Field** | `TypeAttributes` row | A typed attribute on a Definition. Carries one of `FormatRef` / `EnumVersionRef` / `SubTypeVersionRef` / `HelperRef` (mutually exclusive — see §10). |
| **Rule** | `TypeAxioms` row | A natural-language invariant. Field name is `Statement` (renamed from `Description` recently; the plan never asks the user to type "Statement"). |
| **Sample** | `TypeExamples` row | A concrete instance of a Definition. JSON blob. |
| **Choice set** (Enum) | `Enums` + `EnumVersions` + `EnumValues` | A versioned controlled vocabulary. Same Word/Definition/Value shape as Types. |
| **Format** | `Formats` row | A leaf string-shape constraint (regex + length bounds + json-schema-format hint). **Unversioned** — only `ReplacedBy`. Has positive examples *and* counter-examples (`FormatExamples.IsCounter`). |
| **Helper** | `TypeHelpers` + `TypeHelperAttributes` | A reusable shape **scoped to a single Definition** via `OriginTypeVersion` + `OriginPath`. Not independently versioned — it travels with its origin Definition. |
| **Translation** | `Projections` + `ProjectionMappings` | A reusable map between two enum versions. **Unversioned** — identified by its `(FromEnumVersion, ToEnumVersion)` pair. |
| **Migration** | `TypeUpgrades` + `TypeUpgradeOps` (Type side) **and** `EnumUpgrades` + `EnumUpgradeMappings` (Enum side) | The recipe for moving data from one Definition to the next. Two parallel surfaces. |

These editorial terms are **convention-level, not enforced by the rulebook schema** (e.g. `Types.Name` is technically an editable raw field; "Word immutability" is a UX-enforced rule backed by the rulebook's own field descriptions). The Explorer treats them as inviolable.

---

## 2. The guiding principle

> **Every screen offers two affordances: *explore the immutable past* or *fork a new version of what you're looking at*.**

Versions are **the** primary noun for Types and Enums. Editing a published Definition is *never* the right action — the right action is "Fork to next version, edit the draft, promote when ready." The Explorer should make that pattern feel like the path of least resistance everywhere it applies.

For surfaces without version chains (Formats, Projections, Helpers), the corresponding action is different. §9 spells out the three fork flavors; do not pretend they are the same.

Corollary: the UI must make "is this published or a draft?" instantly visible. Color, lock icon, badge — non-negotiable. But this requires a lifecycle the rulebook does not yet populate — see §3.

---

## 3. The lifecycle precondition (must be closed before build)

The whole "draft → published" loop hinges on `TypeVersions.Status` and `EnumVersions.Status`. **As of this writing, all 68 TypeVersions and all 38 EnumVersions have `Status = null`.** The calc fields `IsActive` and `IsDeprecated` exist, but they currently return `false` for everything because nothing has been populated.

Before any Editor work begins, three decisions must land:

1. **Canonical Status vocabulary.** Proposed: `draft` (mutable, unpublished) → `active` (frozen, current) → `deprecated` (frozen, superseded but still readable). Anything else (`retired`?) is rejected — Word-level retirement already lives on `Types.ReplacedBy` / `Enums.ReplacedBy` and shouldn't be re-encoded at the version level.
2. **Backfill rule for the existing nulls.** Every existing TypeVersion / EnumVersion is *de facto* published — they're already referenced from generated SQL, YAML, and Python. The migration is: backfill all current null `Status` to `active` as part of standing up the Explorer.
3. **A new calc field: `IsDraft`.** Defined as `Status="draft"`. Drives the "Edit unlocked" affordance everywhere; absent today.

The Editor enforces:
- "Fork" CTA only appears on rows where `IsDraft=false` (you fork *from* a published Definition).
- "Edit" mode in the right pane (§4) is reachable only when `IsDraft=true`.
- "Promote" transitions a row from `draft` to `active` and is one-way at the rulebook level.

This precondition is load-bearing. If it slips, every other section becomes aspirational.

---

## 4. Three-pane shell

A familiar Postman/Linear/Airtable shape, with a twist on the right pane:

```
┌──────────────┬─────────────────────────┬──────────────────────────────┐
│  NAV TREE    │  LIST / TIMELINE        │  DETAIL / EDITOR             │
│  (vocab,     │  (words in vocab,       │  (definition snapshot,       │
│   activity,  │   versions of a word,   │   field editor,              │
│   pinned)    │   diffs across vers.)   │   axioms, examples, fork CTA)│
└──────────────┴─────────────────────────┴──────────────────────────────┘
```

The **right pane** has a mode toggle: **Read** (rendered docs view of an immutable snapshot, hyperlinked refs, copy-as-JSON) vs. **Edit** (form against a draft Definition, every editable field unlocked). You cannot enter Edit on a non-draft Definition (`IsDraft=false`) — you can only "Fork to /00X" first, which creates a new draft and switches the pane to Edit on that draft.

**Lifecycle badge spec.** Every Definition row, card, and breadcrumb shows a single status pill:

| Status | Pill | Meaning |
|---|---|---|
| `draft` | amber, unlocked icon | Mutable. Editable in the right pane. Not yet promoted. |
| `active` | green, locked icon | Frozen. Read-only. Tip of its Word's chain (usually). |
| `deprecated` | gray, locked icon | Frozen. Superseded by a later version. Still readable for migration purposes. |
| Word-retired (`Types.IsRetired=true`) | red strike-through on the *Word*, not the Definition | Whole Word retired. Inherited by all its Definitions in list views. |

Word-level retirement and Definition-level deprecation are shown distinctly so users don't confuse them.

---

## 5. The journey (the unified path)

A first-time admin developer should fall through this funnel naturally:

1. **Land on the Workbench.** A single dashboard for all users (see §7). Three lanes: *Pick up where you left off* (recent + open drafts), *Browse vocabularies*, *Search the registry*.
2. **Pick a Vocabulary.** Owner profile page: who they are, what they publish (Words / Enums / Formats counts from `TypeCount`, `EnumCount`, `FormatCount` aggregations), recent activity.
3. **Browse what they publish.** Three filterable lists in tabs: **Words**, **Enums**, **Formats**. For Words/Enums, each row shows: latest Definition's version, its status pill (§4), incoming-reference count (`Types`-side `IsUsedAsSubtype` aggregations on `TypeVersions`), and the Word-level retirement flag from `Types.IsRetired` / `Enums.IsRetired`. For Formats, each row shows usage count (`TotalUsageCount`) and the `IsRetired` flag.
4. **Open a Word.** Timeline view of all its Definitions, oldest-to-newest. Each Definition is a card with its status pill, attribute count (`AttributeCount`), axiom count (`AxiomCount`), example count (`ExampleCount`), and a "fork from here" affordance. The current "tip" is highlighted (`IsLeaf` calc). Incoming/outgoing migration arrows (`HasIncomingUpgrade` / `HasOutgoingUpgrade`) annotate each card.
5. **Open a Definition.** Read mode: rendered contract — attributes table (with each `TypeAttribute`'s resolved ref shown via `RefKind`), axioms list (rendered from `TypeAxioms.Statement`), examples gallery (`TypeExamples.ExampleJson`), inbound/outbound migration arrows, "used as sub-type by N other definitions" backlinks (`TotalSubtypeUsageCount`), and any `TypeHelpers` whose `OriginTypeVersion` is this Definition (so helpers are visible from where they live).
6. **Either:**
   - **Stay in Read** — chase a foreign key (a `FormatRef`, an `EnumVersionRef`, a `SubTypeVersionRef`, a `HelperRef`) into the next entity. Pure exploration.
   - **Fork** — primary CTA. The fork pattern depends on what you're forking; see §9. For Types and Enums it pre-fills the next sequential version (`/001` from `/000`) and clones child rows. For Formats it creates a successor and points the old one's `ReplacedBy` at it. For Helpers and Projections, see §9.
7. **Edit the draft.** Every editable field is editable inline. Calculated fields (`IsRetired`, `AttributeCount`, `IsLeaf`, `IsRoot`, `TotalSubtypeUsageCount`, `IncomingUpgradeCount`, `OutgoingUpgradeCount`, `IsClosed`, `RefKind`, …) are surfaced as read-only chips/badges around the form to give the editor real-time feedback. The four-FK exclusivity on `TypeAttributes` (and `TypeHelperAttributes`) is enforced by a single "What does this field reference?" picker — see §10.
8. **Diff before promote.** A side-by-side diff against the source Definition, plus a "scaffold migration" affordance:
   - For Type forks: pre-creates a `TypeUpgrade` (`From`/`To` set) + draft `TypeUpgradeOps` based on the structural delta (added fields, removed fields, type changes, enum-version bumps).
   - For Enum forks: pre-creates an `EnumUpgrade` + draft `EnumUpgradeMappings` based on symbol-set delta.
   - The `OpKind` vocabulary that the scaffolder emits is its own spec (out of scope for this plan, but flagged in §11).
9. **Promote.** Flips `Status` from `draft` to `active`. Now it's part of the immutable past. A confirmation step surfaces calc-field reality checks ("AttributeCount went 12 → 11 — is that intentional?"). Loop back to step 5.

That loop — **explore → land on a definition → fork → edit → diff → promote** — is the whole product for Types and Enums. Everything else is plumbing for it.

---

## 6. Navigation axes (how people slice the registry)

The same 19 tables are reachable from multiple angles. The Explorer should expose all of these as first-class entry points (left nav + URL):

| Axis | Question it answers | Driven by |
|---|---|---|
| **By Vocabulary** | "What does `gridworks-energy` publish?" | `Owners` → `Types` / `Enums` / `Formats` |
| **By Word** | "Show me everything called `bid`." | `Types` → `TypeVersions` |
| **By Definition** | "What's in `bid/002`?" | `TypeVersions` → attrs / axioms / examples |
| **By Field reference** | "Where is `channel.config/000` used as a sub-type?" | `TypeAttributes.SubTypeVersionRef` + `TypeHelperAttributes.SubTypeVersionRef` backlinks (the `IsUsedAsSubtype` and `TotalSubtypeUsageCount` calc fields on `TypeVersions`) |
| **By Format** | "Who uses `uuid4.str`?" | `TypeAttributes.FormatRef` + `TypeHelperAttributes.FormatRef` backlinks (`Formats.TotalUsageCount`) |
| **By Enum** | "Who uses `base.g.node.class/000`?" | `TypeAttributes.EnumVersionRef` + `TypeHelperAttributes.EnumVersionRef` backlinks (`EnumVersions.TotalAttributeUsageCount`) |
| **By Helper** | "Who uses helper `foo`?" | `TypeAttributes.HelperRef` + `TypeHelperAttributes.HelperRef` backlinks (`TypeHelpers.TotalUsageCount`); also reachable from helpers' `OriginTypeVersion` |
| **By Type-Upgrade chain** | "How do I get from `data.channel.gt/000` to `/002`?" | `TypeUpgrades` chained on `FromTypeVersion` / `ToTypeVersion` |
| **By Enum-Upgrade chain** | "How do I get from `boolean.dec/000` to `/001`?" | `EnumUpgrades` chained on `FromEnumVersion` / `ToEnumVersion` |
| **By Translation** | "What does the projection between these two enum versions map?" | `Projections` + `ProjectionMappings` |
| **By Activity** | "What changed this week? What drafts are open?" | `TypeVersions.Created`, `EnumVersions.Created`, `Formats.Created`, `Status=draft` |
| **By Search** | "Find anything named or described as 'tank'." | full-text over `Name` / `Title` / `Description` / `Statement` everywhere |

The left nav tree should default to **By Vocabulary** (the editorial mental model) but expose the others as toggles or peer entry points, not buried in menus.

---

## 7. The Workbench (single dashboard, role-aware accents)

Resist building separate dashboards. One Workbench, three stacked panels:

1. **Resume** — open drafts (rows where `Status="draft"`), recently viewed Definitions, pinned Words.
2. **Vocabularies** — card grid of Owners with counts (`TypeCount`, `EnumCount`, `FormatCount`), recent-version freshness, "drafts open: 3" badges (count of draft `TypeVersions` + `EnumVersions` per Owner).
3. **Activity / Diffs** — chronological feed using `Created` timestamps: newly-promoted Definitions, new Upgrades (Type and Enum), new Projections. Each item links into the relevant detail screen.

Role *accents* (not separate UIs):
- A **schema editor** sees the Drafts panel first.
- A **reviewer** sees Activity first.
- A **migrator** gets a fourth panel: "Open Upgrade chains" — `TypeUpgrades` and `EnumUpgrades` rows whose op/mapping list looks incomplete, or chains that skip versions.

These are panel-ordering preferences, not different routes. Same URLs. Same components.

**Pins and recent-views are not in the rulebook today.** v1 keeps them client-local (browser localStorage, not portable across devices). If they need to become portable, that's a rulebook addition — flagged in §11.

---

## 8. URL spine (the contract for everything else)

Route shape pins the IA. Suggested:

```
/                                   Workbench
/search?q=…
/v/{owner}                          Vocabulary (Owner profile)
/v/{owner}/words                    Words in this vocabulary
/v/{owner}/enums                    Enums in this vocabulary
/v/{owner}/formats                  Formats in this vocabulary
/w/{type-name}                      Word — version timeline
/w/{type-name}/v/{version}          Definition — read mode
/w/{type-name}/v/{version}/edit     Definition — edit mode (drafts only)
/w/{type-name}/v/{version}/diff/{other-version}
/w/{type-name}/fork-from/{version}  Fork action — creates draft + redirects
/enums/{name}                       Enum — version timeline
/enums/{name}/v/{version}
/enums/{name}/v/{version}/edit
/enums/{name}/fork-from/{version}
/formats/{name}                     Format — read
/formats/{name}/edit                Format — edit (only if not retired)
/formats/{name}/replace             Replace action — creates successor + sets old's ReplacedBy
/projections/{name}                 Projection — read
/projections/new?from={ev}&to={ev}  Create projection between two enum versions
/type-upgrades/{type-name}/{from}-to-{to}
/enum-upgrades/{enum-name}/{from}-to-{to}
/helpers/{name}                     Helper — read; opens scoped to its OriginTypeVersion context
/owners/{name}                      alias of /v/{owner}
```

Every detail screen has a **breadcrumb + a "fork"-flavor CTA** in the header (the CTA changes name based on §9 — "Fork", "Replace", "Add helper" — but always lives in the same slot). Every reference (FormatRef, EnumVersionRef, SubTypeVersionRef, HelperRef) renders as a real link. No dead-ends.

---

## 9. The fork action — three flavors (the heart of the app)

The plan's earlier draft asserted "apply the same pattern to Helpers, Formats, Projections." That's wrong — the rulebook gives them genuinely different shapes. Here's the honest breakdown.

### 9a. Versioned fork — Types and Enums

This is the canonical case and the headline interaction.

- **Where it lives:** primary CTA on every Definition detail screen; secondary CTA on the Word timeline ("fork from latest").
- **Default target:** next sequential `NNN` (lookup `MAX(Version) + 1` zero-padded to 3) within the same `Type` / `Enum` parent.
- **What it clones:**
  - **For Types:** the `TypeVersion` row + all `TypeAttributes`, `TypeAxioms`, `TypeExamples` whose `TypeVersion` FK points to the source. New rows have a fresh FK to the new Definition.
  - **For Enums:** the `EnumVersion` row + all `EnumValues` whose `EnumVersion` FK points to the source.
- **What it does NOT clone:** any `TypeUpgrade`/`TypeUpgradeOps` or `EnumUpgrade`/`EnumUpgradeMappings` from prior chains. Instead, after the first edit, it offers "scaffold an upgrade from {source} → {new-draft}" (§5 step 8).
- **Lifecycle:** new row is created with `Status="draft"`. Promote sets `Status="active"`. Promote on a *successor* may optionally set the predecessor's `Status="deprecated"` (configurable; default off, surfaced as a checkbox on promote).
- **Rollback:** delete-draft is the only "undo" — non-draft Definitions are forever. Make this contract explicit in the UI.

### 9b. Successor-only — Formats and Words (Word-level retirement)

Formats have no version chain. Words (Types/Enums) have version chains for their *Definitions* but the Word itself can also be retired wholesale via `ReplacedBy`.

- **Format successor (`/formats/{name}/replace`):** creates a new `Formats` row, points the old one's `ReplacedBy` at it. The old row stays (immutable past); the new row is editable until first usage. There is no version number to bump.
- **Word retirement (`Types.ReplacedBy` / `Enums.ReplacedBy`):** an admin action, not part of the everyday loop. Lives on the Word's settings panel, not the Definition detail. Setting `ReplacedBy` flips `IsRetired=true` and visually retires every Definition in the chain (red strike-through pill — §4).
- **What's cloned:** for Format successors, only the row itself (no child collections except possibly `FormatExamples`, which can be copied as a starting point). For Word retirement, nothing — it's a pointer, not a fork.
- **Rollback:** clear `ReplacedBy` on the predecessor; un-retires.

### 9c. Scoped or pair-keyed — Helpers and Projections

Neither is independently versioned. They don't get a "fork" CTA in the same slot.

- **TypeHelpers** are scoped to a single `OriginTypeVersion`. They are not standalone artifacts; they're effectively named sub-shapes of one Definition. The action on a Helper detail screen is **"Edit helper" (if its origin Definition is a draft) or "Fork the origin Definition first" (if it's not)**. You don't fork a Helper directly — you fork the Definition that owns it, and the helper rows clone with it (extending §9a's clone rule: also clone `TypeHelpers` whose `OriginTypeVersion` points to the source, plus their `TypeHelperAttributes`).
- **Projections** are identified by their `(FromEnumVersion, ToEnumVersion)` pair. The action is **"New projection"** between any two EnumVersions that don't yet have one, not "fork." The detail screen offers an "Edit mappings" affordance that's gated on whether either endpoint EnumVersion is itself a draft (rare — usually projections live between two `active` EnumVersions and are edited freely; they're not part of the published-immutable contract since they're a separate artifact).

The right-pane CTA always lives in the same slot, but its label changes: **Fork** (9a), **Replace** (9b Format), **Retire Word** (9b Word, settings panel), **New projection** (9c Projection), no direct CTA for Helper (9c — go to its origin Definition).

---

## 10. Edit ergonomics (every editable field, editable)

For each table, classify fields:

- **Identity / FK** (`Name`, `Owner`, `Type`, `Enum`, `Version`) — editable only on create; locked after first save.
- **Editable raw** — every other `type: raw` field, editable inline in the right pane.
- **Calculated / aggregation** — surfaced as read-only chips around the form (`IsRetired`, `IsLeaf`, `IsRoot`, `IsActive`, `IsDraft`, `IsDeprecated`, `IsClosed`, `IsUsedAsSubtype`, `AttributeCount`, `IncomingUpgradeCount`, `OutgoingUpgradeCount`, `RefKind`, …). Use them as live feedback, not just decoration.
- **`RawJson` escape hatch** — full JSON editor with schema validation; collapsed by default.

**The four-FK exclusivity rule (must be enforced).** A `TypeAttribute` (and `TypeHelperAttribute`) carries exactly one of:
- `FormatRef` → the value is a string matching a Format
- `EnumVersionRef` → the value is one of an EnumVersion's symbols
- `SubTypeVersionRef` → the value is a nested Definition instance
- `HelperRef` → the value matches a Helper shape

(Or none of the above, in which case `PrimitiveType` carries the shape — `string`, `int`, `bool`, etc.) The calc field `RefKind` resolves which one is set.

The editor must enforce one-of via a single picker — **"What does this field reference?"** with five options (`primitive` / `format` / `enum` / `subtype` / `helper`) — not four independent autocomplete inputs. Switching the picker clears the previous FK and shows the appropriate autocomplete for the chosen kind. The `PrimitiveType` field becomes editable only when `primitive` is selected.

**Child collections** (`TypeAttributes`, `TypeAxioms`, `TypeExamples`, `EnumValues`, `FormatExamples`, `TypeHelperAttributes`, `ProjectionMappings`, `TypeUpgradeOps`, `EnumUpgradeMappings`) get inline table editors with drag-to-reorder for `Idx` fields. Adding a row pre-validates FK targets (autocomplete sourced from the registry itself).

**FormatExamples have two kinds.** The `IsCounter` boolean and the `ExampleKind` calc give us positive examples *and* counter-examples (values the Format must reject). The Format Read screen shows them in two columns; the editor shows them as one table with an `IsCounter` toggle per row.

---

## 11. What this plan deliberately defers

To keep the plan focused on navigation, these are explicitly out of scope for now and worth their own future passes:

- **Auth / write-permissions model** — who can promote a draft, who can retire a Word. The current rulebook has no user concept; `Owners` are organizational, not auth principals.
  - *Architectural note for when this lands.* Because the DAG already computes derived predicates as calc fields on the `vw_*` views, postgres RLS policies become unusually simple: instead of writing JOIN-heavy policies that traverse normalized tables to figure out who can see what, policies can read directly from a calc field — `USING (IsVIP)`, `USING (IsPublished)`, `USING (Owner = current_setting('app.owner'))`. The definition of "what makes someone a VIP / what counts as published / who owns this row" is encapsulated *once* in the rulebook formula and is then transparent to every policy that depends on it. Change the definition, and every policy follows. This is a real benefit of the ERB foundation and should shape the eventual auth design.
- **Concurrent-edit / locking** — what happens when two editors fork the same Definition simultaneously. Trivially: forks always create a new `NNN`, so two simultaneous forks just produce `/001` and `/002` instead of colliding. But two editors editing the same draft is a real problem.
- **The `OpKind` / mapping vocabulary for migration scaffolding** — §5 step 8 hand-waves at "structural delta → pre-filled `TypeUpgradeOps`." Doing this well requires enumerating which `OpKind` values the rulebook supports, which deltas they correspond to, and how `EnumUpgradeMappings` are auto-suggested. Probably the riskiest single piece of the plan; deserves its own spec before implementation.
- **Generated-code preview** — showing what `effortless build` would emit for a draft. Powerful but a layer on top of the Explorer.
- **Bulk operations** — "fork all 12 Words in this vocabulary to next version." Likely needed eventually, deliberately deferred.
- **External publishing** — pushing a promoted Definition to `schemas.electricity.works`.
- **Portable pins / recent-views** — v1 is client-local. If they need to be portable, the rulebook needs a `UserPreferences`-style table (and a User concept first — see auth bullet).
- **Build pipeline integration** — whether the FastAPI server (or its OpenAPI client export) becomes a transpiler entry in [effortless.json](effortless.json). Out of scope for v1; the Explorer runs alongside the build, not inside it.

(Stack itself was previously deferred here; it's now locked — see the Scope blurb at the top and §12 Phase 0.)

---

## 12. Implementation roadmap

A phase-ordered punch list for the agent that picks this up to build. Tasks within a phase can usually go in parallel; phases are gated by their predecessors. References like "(§4)" point back to the section that specifies the behavior.

**Conventions used below:**
- ⛔ = hard gate; nothing downstream works without it.
- 🧱 = touches the rulebook → triggers `effortless build` → must obey the build-discipline rule in `CLAUDE.md` (clean tree before, build commit immediately after, generated-only).
- 🎨 = pure frontend; no rulebook or schema impact.
- 🔌 = data-layer / backend wiring (talks to postgres `vw_*` views).
- ❓ = decision point — surface to the user before proceeding, don't pick silently.

---

### Phase 0 — Decisions (locked) ✅

All five Phase 0 gates resolved as of the third pass. Recorded here so an implementing agent doesn't re-litigate them.

- [x] **Editorial vocabulary** — Vocabulary / Word / Definition / Field / Choice set / Format / Helper / Translation / Migration (§1).
- [x] **Status vocabulary** — `draft` → `active` → `deprecated` (§3). No `retired` at the version level.
- [x] **Stack** — **React + TypeScript** front end; **FastAPI (Python)** back end. Form library: pick during Phase 5 (likely `react-hook-form` + `zod` for the four-FK picker validation, but defer until edit work starts). OpenAPI → typed React client via auto-generation (e.g. `openapi-typescript`).
- [x] **Data path** — FastAPI reads postgres `vw_*` views, writes to base tables. Imports [rulebook-emitters/shared/loader.py](rulebook-emitters/shared/loader.py) for any direct rulebook-JSON reads (schema introspection, `_meta`).
- [x] **Layout** — `app/api/` (FastAPI) + `app/web/` (React + TS), both peer to [postgres/](postgres/) and [rulebook-emitters/](rulebook-emitters/).

### Phase 1 — Lifecycle precondition (🧱 ⛔)

This is the §3 work. Without it, every "draft vs published" affordance in the plan is aspirational.

- [ ] **Add `IsDraft` calc field to `TypeVersions`** in `effortless-rulebook/effortless-rulebook.json`. Formula: `Status = "draft"`. Mirror the existing `IsActive` / `IsDeprecated` shape.
- [ ] **Add `IsDraft` calc field to `EnumVersions`** with the same formula.
- [ ] **Backfill `Status`** on all 68 `TypeVersions` and 38 `EnumVersions` rows in the rulebook JSON's `data[]` arrays: every existing null becomes `"active"`. (See §3 — they're all *de facto* published.)
- [ ] **Run `effortless build`** (clean tree, then commit only the generated output per `CLAUDE.md` build discipline).
- [ ] **Verify in postgres**: `SELECT COUNT(*) FROM vw_TypeVersions WHERE IsActive` should equal 68; same for `vw_EnumVersions` = 38; `IsDraft` = 0 across both.
- [ ] **Confirm with the user** before moving on — Phase 1 is the load-bearing one and merits an explicit "yes, proceed."

### Phase 2 — Project scaffolding (🎨 🔌)

Stand up the empty shell on the locked stack. Reuses [rulebook-emitters/shared/loader.py](rulebook-emitters/shared/loader.py) where possible — see §0.5.

**Backend — `app/api/`:**

- [ ] Initialize a FastAPI project. Suggested layout: `app/api/main.py` (app + router mount), `app/api/routes/` (one module per resource — `owners.py`, `types.py`, `enums.py`, `formats.py`, `helpers.py`, `projections.py`, `upgrades.py`, `search.py`), `app/api/db.py` (psycopg/asyncpg connection helpers), `app/api/models.py` (Pydantic response models), `app/api/loader.py` (re-export from `rulebook_emitters.shared.loader` for direct-JSON reads).
- [ ] Wire the data layer to `postgresql://postgres@localhost:5432/sema`. Smoke test: `GET /api/owners` returns rows from `vw_Owners`.
- [ ] Define hand-rolled Pydantic response models for each of the 23 tables, mirroring `vw_*` view columns. At minimum, the models must surface every calc field the plan references: `IsRetired`, `IsLeaf`, `IsRoot`, `IsActive`, `IsDraft`, `IsDeprecated`, `IsClosed`, `IsUsedAsSubtype`, `RefKind`, `AttributeCount`, `AxiomCount`, `ExampleCount`, `TotalSubtypeUsageCount`, `TotalUsageCount`, `TotalAttributeUsageCount`, `IncomingUpgradeCount`, `OutgoingUpgradeCount`, `HasIncomingUpgrade`, `HasOutgoingUpgrade`, `TypeCount`, `EnumCount`, `FormatCount`, `ExampleKind`. Mark with a `# TODO: replace with rulebook-emitters/python/out/ when emitter graduates`.
- [ ] Verify FastAPI's OpenAPI doc renders at `/docs` and includes every endpoint.
- [ ] Add CORS for the React dev server origin.

**Frontend — `app/web/`:**

- [ ] Initialize a React + TypeScript project (Vite suggested for speed; framework-router optional — Phase 8 URLs are file-system-friendly under either Next.js or React Router).
- [ ] Auto-generate a typed client from FastAPI's OpenAPI schema (e.g. `openapi-typescript` + a thin fetch wrapper, or `openapi-fetch`). Wire it to call the FastAPI dev server.
- [ ] Implement the URL routing skeleton matching §8. Every route renders a placeholder; goal is to lock the URL contract before screens land.
- [ ] Build a generic three-pane shell layout component (§4). Empty panels, real slots.

**Cross-cutting:**

- [ ] Decide on a single `app/` README that documents how to run both halves (FastAPI dev server + Vite/Next dev server) and how the typed-client regen works.
- [ ] Commit the scaffold as one or two commits, separate from any rulebook work.

### Phase 3 — Read-only navigation (🎨 🔌)

The "explore the immutable past" half of §2. No editing yet. After Phase 3, the Explorer is a competent read-only tool — that's a useful checkpoint.

- [ ] **Workbench** (§7): three stacked panels (Resume, Vocabularies, Activity). Resume reads `Status="draft"` rows (will be empty until Phase 5); Vocabularies grids `Owners` with `TypeCount` / `EnumCount` / `FormatCount`; Activity feeds from `Created` timestamps across `TypeVersions` / `EnumVersions` / `Formats` / `TypeUpgrades` / `EnumUpgrades` / `Projections`.
- [ ] **Vocabulary (Owner) page** at `/v/{owner}` — counts, recent activity, three tabs (Words / Enums / Formats).
- [ ] **Word timeline** at `/w/{type-name}` — list of `TypeVersions` oldest-to-newest with status pills (§4), `AttributeCount` / `AxiomCount` / `ExampleCount`, `IsLeaf` highlight, `HasIncomingUpgrade` / `HasOutgoingUpgrade` annotations.
- [ ] **Definition detail (Read mode)** at `/w/{type-name}/v/{version}`: attributes table with `RefKind`-driven rendering for each `TypeAttribute`, axioms list (`Statement`), examples gallery (`ExampleJson`), inbound migration arrows, `TotalSubtypeUsageCount` backlinks, `TypeHelpers` whose `OriginTypeVersion` is this Definition.
- [ ] **Enum timeline + detail** at `/enums/{name}` and `/enums/{name}/v/{version}` — mirror of Word/Definition for `Enums` / `EnumVersions` / `EnumValues`.
- [ ] **Format detail** at `/formats/{name}` — read-only view including positive examples and counter-examples (`FormatExamples.IsCounter` split into two columns per §10).
- [ ] **Helper detail** at `/helpers/{name}` — opens scoped to its `OriginTypeVersion`; displays `TypeHelperAttributes` like an attribute table.
- [ ] **Projection detail** at `/projections/{name}` — shows `ProjectionMappings` between the two `EnumVersion` endpoints.
- [ ] **Lifecycle badges** (§4): Status pill component used everywhere a Definition is rendered (row, card, breadcrumb). Word-level retirement renders as red strike-through on the *Word* in list views, distinct from version-level deprecation.
- [ ] **Reference links** (§8 contract): every `FormatRef` / `EnumVersionRef` / `SubTypeVersionRef` / `HelperRef` renders as a real link. No dead-ends.
- [ ] **Search** at `/search?q=…` — full-text over `Name` / `Title` / `Description` / `Statement` per §6's "By Search" axis.

**Phase 3 done =** an admin can land on the Workbench, click into any vocabulary, traverse to any Definition, follow every reference, and never hit a dead-end. No edit affordances yet.

### Phase 4 — Navigation axes & backlinks (🎨 🔌)

§6 is the slicing surface. Phase 3 covered "By Vocabulary" / "By Word" / "By Definition" implicitly; this phase makes the others first-class.

- [ ] **By Field reference** — backlink panels on `TypeVersion` detail driven by `IsUsedAsSubtype` / `TotalSubtypeUsageCount`.
- [ ] **By Format** — backlink panel on Format detail driven by `Formats.TotalUsageCount`.
- [ ] **By Enum** — backlink panel on `EnumVersion` detail driven by `TotalAttributeUsageCount`.
- [ ] **By Helper** — backlink panel on Helper detail driven by `TotalUsageCount`.
- [ ] **By Type-Upgrade chain** — chain visualization on `/type-upgrades/{type-name}/{from}-to-{to}` and inbound/outbound arrows on Definition detail.
- [ ] **By Enum-Upgrade chain** — same shape for `EnumUpgrades`.
- [ ] **By Activity** — already built in Workbench; expose a full view at `/activity` with filters (vocab, table, date).
- [ ] **Pins / recent-views** — client-local (browser localStorage) per §7. Not portable across devices; documented as a v1 limitation.

### Phase 5 — Edit mode + the four-FK picker (🎨 🔌)

Half of §2 — the "fork a new version" affordance starts to come alive. But editing only works on drafts, and Phase 5 doesn't *create* drafts yet (that's Phase 6). The point of Phase 5 is to build the edit surface against any draft we manually create.

- [ ] **Right-pane mode toggle** (§4): Read / Edit. Edit is only reachable when `IsDraft=true`.
- [ ] **Inline form fields** for every `type: raw` editable field per §10 (identity / FK fields locked after first save).
- [ ] **Calc-field chips** rendered around the form: `IsRetired`, `IsLeaf`, `IsRoot`, `IsActive`, `IsDraft`, `IsDeprecated`, `IsClosed`, `IsUsedAsSubtype`, `AttributeCount`, `IncomingUpgradeCount`, `OutgoingUpgradeCount`, `RefKind`. Read-only, live-updated as the form saves.
- [ ] **The "What does this field reference?" picker** (§10 — non-negotiable). Single picker with five options (`primitive` / `format` / `enum` / `subtype` / `helper`). Switching clears prior FK and swaps the autocomplete. `PrimitiveType` is editable only when `primitive` is selected. Applies to both `TypeAttributes` and `TypeHelperAttributes`.
- [ ] **Child collection editors** (§10): inline tables for `TypeAttributes`, `TypeAxioms`, `TypeExamples`, `EnumValues`, `FormatExamples`, `TypeHelperAttributes`, `ProjectionMappings`, `TypeUpgradeOps`, `EnumUpgradeMappings`. Drag-to-reorder updates `Idx`. Add-row pre-validates FK targets via registry-sourced autocomplete.
- [ ] **`FormatExamples` editor** with `IsCounter` toggle per row (positive vs counter-example).
- [ ] **`RawJson` escape hatch** — full JSON editor with schema validation, collapsed by default.
- [ ] **Manual draft creation** for testing this phase: write a small admin-only script (or use direct SQL) to flip one `TypeVersion` to `Status="draft"` and verify the form unlocks.

**Phase 5 done =** given a draft Definition, an admin can edit every field per §10's rules, including the four-FK exclusivity. No fork action yet.

### Phase 6 — The fork action, three flavors (🎨 🔌)

§9 is the heart of the app. Each flavor is a distinct write path.

- [ ] **9a Versioned fork — Types** (`/w/{type-name}/fork-from/{version}`): inserts a new `TypeVersions` row at `MAX(Version)+1`; clones `TypeAttributes` / `TypeAxioms` / `TypeExamples` and `TypeHelpers` (+ their `TypeHelperAttributes`) whose FK points to the source; sets new row's `Status="draft"`; redirects to the draft's edit URL.
- [ ] **9a Versioned fork — Enums** (`/enums/{name}/fork-from/{version}`): mirrors Types. Inserts new `EnumVersions` row, clones `EnumValues`.
- [ ] **9b Format successor** (`/formats/{name}/replace`): inserts new `Formats` row, points the predecessor's `ReplacedBy` at it. Optionally clones `FormatExamples` as a starting point. New row is editable until first usage.
- [ ] **9b Word retirement** — admin action on the Word's settings panel (not the Definition detail): sets `Types.ReplacedBy` / `Enums.ReplacedBy`. Verifies the cascade — `IsRetired` flips, list views render strike-through.
- [ ] **9c New projection** (`/projections/new?from={ev}&to={ev}`): inserts a new `Projections` row given a `(FromEnumVersion, ToEnumVersion)` pair that doesn't yet exist; redirects to its edit URL.
- [ ] **9c Helper editing** — no direct fork CTA. On a Helper detail screen: if its `OriginTypeVersion` is a draft, "Edit helper" is enabled; otherwise the CTA is "Fork the origin Definition" which redirects to 9a on the parent Definition.
- [ ] **CTA slot in the right-pane header** — a single component whose label changes per flavor: **Fork** / **Replace** / **Retire Word** / **New projection** / no-direct-CTA-for-Helper. Always lives in the same slot (§9 close).
- [ ] **Delete-draft affordance** — the only "undo" for 9a forks per §9a. Surfaced explicitly with a confirmation that names the contract: "Non-draft Definitions are forever."

### Phase 7 — Diff + Promote (🎨 🔌)

§5 step 8 and step 9. Closes the loop.

- [ ] **Diff view** at `/w/{type-name}/v/{version}/diff/{other-version}` — side-by-side render of two Definitions: added fields / removed fields / changed `RefKind` / changed enum-version bumps / changed `Statement` / changed examples.
- [ ] **Promote action** — flips `Status` from `draft` to `active`. Confirmation step surfaces calc-field reality checks ("AttributeCount went 12 → 11 — is that intentional?").
- [ ] **Optional predecessor deprecation** — checkbox on Promote to set predecessor's `Status="deprecated"`. Default off.
- [ ] **Post-promote** — UI redirects to the now-active Definition in Read mode. Confirms the "promote is one-way" contract — surfaces it in copy.

**Phase 7 done =** the full §5 loop works end-to-end for Types and Enums: explore → land → fork → edit → diff → promote → loop.

### Phase 8 — Migration scaffolding (🎨 🔌, depends on a separate spec — see §11)

⚠️ This phase has a hard prerequisite: **the `OpKind` vocabulary spec** (§11). Do not start until that spec exists. If the spec doesn't ship in time, ship Phase 7 without Phase 8 and surface migrations as manual-only.

- [ ] **`OpKind` vocabulary spec** — out-of-band deliverable. Enumerate which `OpKind` values exist on `TypeUpgradeOps`, what structural delta each corresponds to, and the analogous mapping vocabulary for `EnumUpgradeMappings`.
- [ ] **`TypeUpgrade` scaffolder** — invoked from the diff view (Phase 7). Pre-creates a `TypeUpgrade` (`From` / `To` set) plus draft `TypeUpgradeOps` based on the structural delta.
- [ ] **`EnumUpgrade` scaffolder** — symmetric, emits draft `EnumUpgradeMappings` based on symbol-set delta.
- [ ] **Manual `TypeUpgradeOps` / `EnumUpgradeMappings` editor** — already covered by Phase 5's child-collection editor; verify it covers the auto-scaffolded rows too.

### Phase 9 — Polish (🎨)

Things you don't notice when present, but feel cheap when missing.

- [ ] Keyboard shortcuts for nav-tree traversal and pane switching.
- [ ] Empty states for every list (no Owners / no Words / no drafts).
- [ ] Loading + error states on every async surface.
- [ ] Copy-as-JSON on every Definition Read view.
- [ ] Print-friendly Definition view (Read mode) — useful for review handoffs.

---

### Risks the agent should flag early

If any of these are encountered during build, stop and surface to the user — they are the most likely cracks in the plan:

1. **Phase 1 backfill is noisier than expected.** If some of the 68 TypeVersions or 38 EnumVersions turn out to be *not* truly published (e.g. abandoned), the blanket `active` backfill is wrong. Audit before flipping.
2. **The four-FK exclusivity rule isn't actually enforced anywhere in the rulebook today** (§10 enforces it as UX). If existing data violates it (a row with both `FormatRef` and `EnumVersionRef`), the picker breaks. Run a pre-build audit query.
3. **`TypeHelpers` clone semantics in 9a forks** are spec'd here but never tested. The first fork that involves a Definition with helpers is the canary — verify the cloned helpers point at the new `TypeVersion`, not the old one.
4. **Projections between two `active` EnumVersions are edited freely** (§9c) — i.e. they're a separate immutability contract from the Word/Definition one. If anyone expects projections to be frozen alongside their endpoint EnumVersions, that's a misunderstanding to surface.
5. **The `OpKind` spec gating Phase 8** — if it slips, do not invent `OpKind` values; ship without scaffolding instead.

---

## How to use this plan

This is the spine. §12 is the detailed roadmap; this is the order of operations at a glance:

1. **Phase 1 first (rulebook).** Resolve §3: add `IsDraft` calc fields to `TypeVersions` and `EnumVersions`, backfill all current null `Status` values to `active`, run `effortless build`, verify in postgres. This is rulebook work, no app code yet — and per [CLAUDE.md](CLAUDE.md), the build commit must contain only generated output.
2. **Phase 2 (scaffold).** Stand up `app/api/` (FastAPI) and `app/web/` (React + TS) per §12 Phase 2. Smoke test the FastAPI → postgres path and the React → FastAPI typed-client path. URL skeleton in place per §8.
3. **Phase 3 (read-only Explorer).** Build the navigation surface end-to-end against postgres `vw_*` views. After Phase 3, the Explorer is a competent read-only registry browser — useful even before any edit features land.
4. **Phases 4–7 (the loop).** Backlinks → edit forms → fork actions → diff/promote. Closes the §5 loop.
5. **Phase 8 (migrations).** Gated on the `OpKind` vocabulary spec — see §11. Ship Phase 7 without it if needed.

The editorial vocabulary (§1), Status vocabulary (§3), and stack (Scope blurb + §12 Phase 0) are all locked in this pass. The first agent to start implementation should begin at Phase 1.
