# Registry Explorer — Navigation Plan

> **Scope.** This plan defines the navigation architecture and UX guiding principles for an `/app/` version of the sema Registry Explorer — an admin-developer tool for seeing, editing, managing, navigating, exploring, documenting, and expanding the entire sema model. It is *only* a navigation/IA plan; it does not pick a stack, design components in detail, or specify backend wiring. Treat it as the spine that everything else hangs off of.
>
> **Audience for now.** Administrative-level developers who need full-surface access to the registry. Future role-tailoring is discussed in §6, but the v1 surface is unified.
>
> **Status.** Draft for review. Intended to be vetted in a separate conversation/agent before any implementation work begins.

---

## 1. The mental model (and what to call things)

Before navigation, we need names. The rulebook's nouns are technical (`Owners`, `Types`, `TypeVersions`...). The Explorer should let users think in editorial terms:

| Editorial term | Rulebook entity | What it is |
|---|---|---|
| **Vocabulary** | `Owners` row | A namespace authored by one org/person (`gridworks-energy`, `microerapower`, …) |
| **Word** | `Types` row | An immutable name (`bid`, `channel.config`, `report`). Lives forever; can only be retired via `ReplacedBy`. |
| **Definition** | `TypeVersions` row | A frozen snapshot of what that Word meant at version `NNN` (`bid/000`, `bid/001`…). The unit of forking. |
| **Field** | `TypeAttributes` row | A typed attribute on a Definition. |
| **Rule** | `TypeAxioms` row | A natural-language invariant. |
| **Sample** | `TypeExamples` row | A concrete instance of a Definition. |
| **Translation** | `Projections` + `ProjectionMappings` | A reusable map between two enum versions (or value spaces). |
| **Migration** | `TypeUpgrades` + `TypeUpgradeOps` | The recipe for moving data from one Definition to the next. |

(Enums/EnumVersions/EnumValues, Formats, and TypeHelpers/TypeHelperAttributes parallel Words/Definitions/Fields and get the same treatment.)

These are suggestions — pick whatever vocabulary matches how the team already talks. The point is: **names that match an editorial mindset, not a DB mindset**.

## 2. The guiding principle

> **Every screen offers two affordances: *explore the immutable past* or *fork a new version of what you're looking at*.**

Versions are **the** primary noun. Every Word, Enum, Projection, and Upgrade lives as a chain of frozen Definitions. Editing a published Definition is *never* the right action — the right action is "Fork to next version, edit the draft, promote when ready." The Explorer should make that pattern feel like the path of least resistance everywhere.

Corollary: the UI must make "is this published or a draft?" instantly visible. Color, lock icon, badge — non-negotiable.

## 3. Three-pane shell

A familiar Postman/Linear/Airtable shape, with a twist on the right pane:

```
┌──────────────┬─────────────────────────┬──────────────────────────────┐
│  NAV TREE    │  LIST / TIMELINE        │  DETAIL / EDITOR             │
│  (vocab,     │  (words in vocab,       │  (definition snapshot,       │
│   activity,  │   versions of a word,   │   field editor,              │
│   pinned)    │   diffs across vers.)   │   axioms, examples, fork CTA)│
└──────────────┴─────────────────────────┴──────────────────────────────┘
```

The **right pane** has a mode toggle: **Read** (rendered docs view of an immutable snapshot, hyperlinked refs, copy-as-JSON) vs. **Edit** (form against a draft Definition, every editable field unlocked). You cannot enter Edit on a published Definition — you can only "Fork to /00X" first.

## 4. The journey (the unified path)

A first-time admin developer should fall through this funnel naturally:

1. **Land on the Workbench.** A single dashboard for all users (see §6). Three lanes: *Pick up where you left off* (recent + drafts), *Browse vocabularies*, *Search the registry*.
2. **Pick a Vocabulary.** Owner profile page: who they are, what they publish, counts of Words/Enums/Formats, recent activity.
3. **Browse the Words.** Filterable list. Each row shows: latest version, published vs. draft state, count of incoming references (using the `IsUsedAsSubtype` / aggregation calc fields already in the rulebook), retired flag.
4. **Open a Word.** Timeline view of all its Definitions, oldest-to-newest. Each Definition is a card with status, attribute count, axiom count, "fork from here" affordance. The current "tip" is highlighted (`IsLeaf` calc).
5. **Open a Definition.** Read mode: rendered contract — attributes table, axioms list, examples gallery, inbound/outbound upgrade arrows, "used as sub-type by N other definitions" backlinks.
6. **Either**:
   - **Stay in Read** — chase a foreign key (a `FormatRef`, an `EnumVersionRef`, a `SubTypeVersionRef`) into the next Definition. Pure exploration.
   - **Fork** — primary CTA. Pre-fills the next sequential version (`/001` from `/000`), clones every TypeAttribute / TypeAxiom / TypeExample, opens the new draft in Edit mode in the right pane.
7. **Edit the draft.** Every editable field is editable inline. Calculated fields (`IsRetired`, `AttributeCount`, `IsLeaf`, `TotalSubtypeUsageCount`, etc.) are surfaced as read-only chips/badges around the form to give the editor real-time feedback on what they're doing.
8. **Diff before promote.** A side-by-side diff against the source Definition, plus a "scaffold migration" affordance that pre-creates a `TypeUpgrade` + draft `TypeUpgradeOps` based on the structural delta (added fields, removed fields, type changes).
9. **Promote.** Freezes the draft. Now it's part of the immutable past. Loop back to step 5.

That loop — **explore → land on a definition → fork → edit → diff → promote** — is the whole product. Everything else is plumbing for it.

## 5. Navigation axes (how people slice the registry)

The same 19 tables are reachable from multiple angles. The Explorer should expose all of these as first-class entry points (left nav + URL):

| Axis | Question it answers | Driven by |
|---|---|---|
| **By Vocabulary** | "What does `gridworks-energy` publish?" | `Owners` → `Types`/`Enums`/`Formats` |
| **By Word** | "Show me everything called `bid`." | `Types` → `TypeVersions` |
| **By Definition** | "What's in `bid/002`?" | `TypeVersions` → attrs/axioms/examples |
| **By Field reference** | "Where is `channel.config/000` used as a sub-type?" | `TypeAttributes.SubTypeVersionRef` backlinks (the `IsUsedAsSubtype` calc field) |
| **By Format** | "Who uses `uuid4.str`?" | `TypeAttributes.FormatRef` backlinks |
| **By Enum** | "Who uses `base.g.node.class/000`?" | `TypeAttributes.EnumVersionRef` backlinks |
| **By Upgrade chain** | "How do I get from `data.channel.gt/000` to `/002`?" | `TypeUpgrades` chained on `From`/`To` |
| **By Translation** | "What does `SpaceheatTelemetryQuantityProjection` map?" | `Projections` + `ProjectionMappings` |
| **By Activity** | "What changed this week? What drafts are open?" | `TypeVersions.Created`, draft status |
| **By Search** | "Find anything named or described as 'tank'." | full-text over `Name`/`Title`/`Description` everywhere |

The left nav tree should default to **By Vocabulary** (the editorial mental model) but expose the others as toggles or peer entry points, not buried in menus.

## 6. The Workbench (single dashboard, role-aware accents)

Resist building separate dashboards. One Workbench, three stacked panels:

1. **Resume** — drafts in progress (yours, then everyone's), recently viewed Definitions, pinned Words.
2. **Vocabularies** — card grid of Owners with counts, recent-version freshness, "drafts open: 3" badges.
3. **Activity / Diffs** — chronological feed of newly-promoted Definitions, new Upgrades, new Projections. Each item links into the Definition detail.

Role *accents* (not separate UIs):
- A **schema editor** sees the Drafts panel first.
- A **reviewer** sees Activity first.
- A **migrator** gets a fourth panel: "Open Upgrade chains" — `TypeUpgrades` rows whose ops list looks incomplete, or chains that skip versions.

These are panel-ordering preferences, not different routes. Same URLs. Same components.

## 7. URL spine (the contract for everything else)

Route shape pins the IA. Suggested:

```
/                                  Workbench
/search?q=…
/v/{owner}                         Vocabulary (Owner profile)
/v/{owner}/words                   Words in this vocabulary
/v/{owner}/enums
/v/{owner}/formats
/w/{type-name}                     Word — version timeline
/w/{type-name}/v/{version}         Definition — read mode
/w/{type-name}/v/{version}/edit    Definition — edit mode (drafts only)
/w/{type-name}/v/{version}/diff/{other-version}
/w/{type-name}/fork-from/{version} Fork action — creates draft + redirects
/enums/{name}                      Enum — version timeline
/enums/{name}/v/{version}
/formats/{name}
/projections/{name}
/upgrades/{type-name}/{from}-to-{to}
/helpers/{name}
/owners/{name}                     alias of /v/{owner}
```

Every detail screen has a **breadcrumb + a "fork" CTA** in the header. Every reference (FormatRef, EnumVersionRef, SubTypeVersionRef) renders as a real link. No dead-ends.

## 8. The fork action — the heart of the app

Define this carefully because it's the headline interaction:

- **Where it lives:** primary CTA on every Definition detail screen; secondary CTA on the Word timeline ("fork from latest").
- **Default target:** next sequential `NNN` (lookup `MAX(Version) + 1` zero-padded to 3).
- **What it clones:** the `TypeVersion` row + all `TypeAttributes`, `TypeAxioms`, `TypeExamples` whose `TypeVersion` FK points to the source. (Same shape for Enums → `EnumValues`; Helpers → `TypeHelperAttributes`.)
- **What it does NOT clone:** `TypeUpgrade`/`TypeUpgradeOps` from prior chains. Instead, it offers a "scaffold an upgrade from {source} → {new-draft}" affordance after the first edit.
- **Lifecycle states:** `draft` (mutable) → `published` (immutable). Status field already exists on `TypeVersion`. Add a confirmation step on promote that surfaces calc-field reality checks ("AttributeCount went 12 → 11 — is that intentional?").
- **Rollback:** delete-draft is the only "undo" — published Definitions are forever. Make this contract explicit in the UI.

Apply the same pattern, with appropriate adjustments, to: **Enums**, **Formats** (no version chain — they only have `ReplacedBy`, so "fork" means "create a successor and point my old one at it"), **Projections**, **TypeHelpers**.

## 9. Edit ergonomics (every editable field, editable)

For each table, classify fields:

- **Identity / FK** (`Name`, `Owner`, `Type`, `Version`) — editable only on create; locked after first save.
- **Editable raw** — every other `type: raw` field, editable inline in the right pane.
- **Calculated / aggregation** — surfaced as read-only chips around the form (`IsRetired`, `IsLeaf`, `IsRoot`, `IsUsedAsSubtype`, `AttributeCount`, `IncomingUpgradeCount`, …). Use them as live feedback, not just decoration.
- **`RawJson` escape hatch** — full JSON editor with schema validation; collapsed by default.

Child collections (`TypeAttributes`, `TypeAxioms`, `TypeExamples`) get inline table editors with drag-to-reorder for `Idx` fields. Adding a row pre-validates FK targets (FormatRef autocomplete, EnumVersionRef autocomplete, SubTypeVersionRef autocomplete — all sourced from the registry itself).

## 10. What this plan deliberately defers

To keep the plan focused on navigation, these are explicitly out of scope for now and worth their own future passes:

- **Auth / write-permissions model** — who can promote a draft. (The current rulebook has no user concept; `Owners` are organizational, not auth principals.)
- **Concurrent-edit / locking** — what happens when two editors fork the same Definition simultaneously.
- **Generated-code preview** — showing what `effortless build` would emit for a draft. Powerful but a layer on top of the Explorer, not part of it.
- **Bulk operations** — "fork all 12 Words in this vocabulary to next version." Likely needed eventually, deliberately deferred.
- **External publishing** — pushing a promoted Definition to `schemas.electricity.works`.
- **Stack / framework choice** — frontend framework, backend (talking to postgres `vw_*` views vs. the rulebook JSON directly), build pipeline integration. Pick after the IA is signed off.

---

## How to use this plan

This is meant to be the spine. Next steps would be:
1. Confirm the vocabulary (Vocabulary / Word / Definition / Field) — or replace with the team's preferred terms.
2. Wireframe the **Workbench**, the **Word timeline**, and the **Definition detail (read + edit + diff)** — three screens that exercise the whole pattern.
3. Spec the **fork action** in detail (the SQL writes it triggers, the redirect, the diff scaffolding).
4. Then, and only then, talk frameworks and stack.
