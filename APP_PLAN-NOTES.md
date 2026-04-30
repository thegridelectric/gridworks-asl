# Minor suggestions for the implementing agent

> Companion to [APP_PLAN.md](APP_PLAN.md). The plan is canonical; this file is a heads-up about things that landed *after* the plan was written and a few open questions worth noticing before you commit to a design choice. Read once, then go back to the plan.

---

## 1. Phase 1.5 happened — the schema is richer than the plan implies

The plan refers to calc fields like `IsPromotable`, `HasStaleReferences`, `RefIsStale`, `OwnerName` as if they're aspirational. **They exist now.** Commits `518ac4b` + `2e5ab4e` added 89 calc/lookup/aggregation fields across 19 tables to back the §4–§10 storytelling surfaces. The mock-data sweep in commit `1db7a05` populated drafts, retirement, deprecation, and the empty owners. You can query everything in the table below today.

| When the plan tells you to render… | …read this from `vw_*` |
|---|---|
| Vocabulary card "drafts open: N" badge (§7) | `vw_owners.{draft_type_version_count, draft_enum_version_count, has_open_drafts}` |
| Word card draft/active/deprecated split (§5 step 3) | `vw_types.{draft_version_count, active_version_count, deprecated_version_count, has_drafts}` |
| Lifecycle pill on a Definition row (§4) | `vw_type_versions.{is_draft, is_active, is_deprecated, word_is_retired}` — four independent flags, never confused |
| Promote-button gate (§7) | `vw_type_versions.is_promotable` (= `IsDraft AND NOT HasStaleReferences AND AttributeCount>0`) |
| Per-attribute "this ref is broken" warning (§10) | `vw_type_attributes.{ref_is_stale, ref_format_is_retired, ref_enum_is_draft, ref_subtype_word_is_retired, …}` |
| Owner / Word display on a TypeVersion row | `vw_type_versions.{owner_name, word_title}` (lookups; no JOIN needed) |

There's a real stale-ref demo in the data: **`bid/000.MarketSlotName`** points at the now-retired `market.slot.name` format. Query `vw_type_versions WHERE name='bid/000'` and you'll see `has_stale_references=TRUE`, `stale_reference_count=1`. That row is the canary for the whole §10 picker UX.

## 2. There's a transpiler-bug landmine. Tooling defuses it; don't let a build silently re-arm it.

`rulebook-to-postgres v2026.04.30.0131` has two latent bugs that bit during Phase 1.5:

1. **Lookups join by `<target_table>_id` (UUID PK) instead of by Name.** This rulebook stores FKs by Name. The generated `INDEX/MATCH` body matches a UUID column against a Name string → all lookups return NULL.
2. **`COUNTIFS`/`MAXIFS`/`MINIFS`/`SUMIFS` silently drop criteria-range pairs when the criteria column is calc/lookup.** Owner draft-counts came out as uniformly `1` for every owner.

Fixed by [scripts/fix_lookup_functions.py](scripts/fix_lookup_functions.py) and [scripts/fix_aggregations.py](scripts/fix_aggregations.py), which append corrected function bodies to [postgres/02b-customize-functions.sql](postgres/02b-customize-functions.sql). They are idempotent.

**Run after every `effortless build`:**
```bash
effortless build
python3 scripts/fix_lookup_functions.py
python3 scripts/fix_aggregations.py
cd postgres && ./init-db.sh
```

**Canary symptom** that the workaround didn't run: `SELECT name, draft_type_version_count FROM vw_owners` returns `1` for every owner. Don't chase it as a FastAPI bug — it's the transpiler regenerating a broken `02b-customize-functions.sql`.

(Worth filing both bugs upstream eventually. Clean repros live in commit `8eab1d8`.)

## 3. Three open questions you'll hit and don't need to answer alone

- **Where does deprecation-reconciliation eventually live?** Today the rule "promoting `bid/001` deprecates `bid/000`" is enforced by [scripts/add_explorer_mock_data.py](scripts/add_explorer_mock_data.py)'s M3 step (iterative graph walk). Fine for mock data; wrong for the Promote action in §7. Probably wants to become a postgres function called by FastAPI on promote. Flag it when you get to Phase 7.
- **Orphan: `gw.nolan.layout` has `Owner=null`.** It exists in `vw_types` but won't show up under any Vocabulary in §7's grid. Either assign an owner or delete the row before Phase 3 ships, or your "list all words" query has a homeless row.
- **`OpKind` vocabulary spec gates Phase 8.** Plan §11 already flags this. Worth deciding parallel-track vs. defer *before* you start Phase 7's diff view, since the diff view's "scaffold migration" affordance is downstream.

## 4. The deprecation reconciliation rule (so you don't re-derive it)

Used in mock data, will be useful in the Promote service:

> A `TypeVersion` is `deprecated` iff some `TypeUpgrade` chain leads forward from it to an `active` (non-draft) descendant. Equivalently: deprecated iff there is an outgoing `TypeUpgrade` whose target is **not** `draft`. Iterate to convergence so multi-step chains (`/000→/001→/002`) settle correctly. Predecessors of `draft` successors stay `active` until promote.

This is why `bid/000` is currently `active` despite having an outgoing `TypeUpgrade` to `bid/001` — `/001` is a draft. When `/001` promotes, `/000` flips to `deprecated` automatically.

## 5. Don't be surprised by

- **`relay.closed.or.open` is both retired AND has a draft `/001`.** Editorially weird but real: a Word can be retired (the whole vocabulary moves on) while a draft of one of its versions exists in flight. The Explorer's badge spec handles this: red strike-through on the *Word*, amber pill on the *draft Version*.
- **Mock timestamps cluster on 2026-04-30.** All Phase 1.5 mock additions share `Created = 2026-04-30T18:00:00Z`. If your Activity feed sort looks like a tower at one timestamp, that's why.
- **Status counts:** 50 active TypeVersions / 20 deprecated / 3 draft. 39 active EnumVersions / 0 deprecated / 2 draft. 1 retired Word in each of {Type, Enum, Format}. Six populated Owners. Use these as smoke-test reference numbers.
