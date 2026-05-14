# effortless-rulebook/

This folder holds **`effortless-rulebook.json`** — a CMCC instance describing sema's type / enum / format / version-upgrade ontology. This README captures the architectural context: what the rulebook is, where it sits in the larger stack, and how it relates to the GridWorks SOW signed 2026-05-01.

---

## What this file actually is

`effortless-rulebook.json` is not just a project artifact. It is a **CMCC instance** — a serialization of a Conceptual Model Completeness Conjecture model.

CMCC (Edward Sturms / eejai42, published on Zenodo) posits that any computable rule, in any domain, can be captured declaratively with **five primitives** in an ACID-compliant environment:

1. **Schema** — entity/table definitions
2. **Data** — rows
3. **Lookups** — cross-references between rows
4. **Aggregations** — sums, counts, rollups
5. **Calculated / Formula Fields** — derived values, axioms, predicates

CMCC is argued to be **Turing-complete**, equivalent in expressive power to Lambda Calculus and Rule 110, and has been applied across business rules, financial regulations, manufacturing, biology/signaling pathways, genetics, physics, and quantum logic.

The structure of this JSON file (top-level table objects, each with a `schema[]` and `data[]` array, with field types `raw` / `calculated` / `lookup` / `relationship` / `aggregation`) is exactly the five primitives in serializable form.

References:
- [CMCC as a Universal Computational Framework (Zenodo)](https://zenodo.org/records/14761025)
- [The CMCC Meets the Ruliad (Medium)](https://medium.com/conceptual-model-completeness-conjecture-cmcc/the-cmcc-meets-the-ruliad-a8d7035757ac)
- [Why CMCC Transcends Traditional MDE (Medium)](https://medium.com/@eejai42/why-the-conceptual-model-completeness-conjecture-cmcc-transcends-traditional-model-driven-241ba020031a)

---

## Where it sits in the stack

```
                   ┌─────────────────────────────────────────────┐
                   │  CMCC (formal framework — 5 primitives)     │
                   └────────────────────┬────────────────────────┘
                                        │ instance of
                                        ▼
   ┌───────────────────────────────────────────────────────────────┐
   │  effortless-rulebook.json   (this folder — sema's CMCC inst.) │
   └───────────────┬─────────────────────────────────────────┬─────┘
                   │                                         │
        ssotme:// transpilers                       (future) emitters
                   │                                         │
   ┌───────────────┴─────────┐               ┌───────────────┴────────────────┐
   │ rulebook-to-postgres    │               │ rulebook-to-yaml (round-trip)  │
   │ rulebook-to-yaml        │               │ rulebook-to-python (planned)   │
   │ rulebook-to-html / api  │               │ rulebook-to-go     (planned)   │
   └─────────────────────────┘               │ rulebook-to-js     (planned)   │
                                             └────────────────────────────────┘
```

- **CMCC** is the math.
- **`effortless-rulebook.json`** is the data — a versioned, declarative source of truth for sema's vocabulary.
- **ssotme://** is the operational protocol — *"like Git, but for business logic"*. The `effortless` CLI (also known as `ssotme` / `aicapture` / `aic`) transports the rulebook and runs transpilers against it.
- **Transpilers** are deterministic projections from a CMCC instance to a target (postgres, yaml, python, go, js, html).
- **EffortlessAPI** (effortlessapi.com) is the hosted runtime that can serve a rulebook as a live, zero-code API.

References:
- [SSoTme GitHub organization](https://github.com/SSoTme)
- [Effortless ecosystem (transpiler catalog)](https://github.com/effortlessapi)
- [Executive Summary: CMCC (Medium)](https://medium.com/effortlessapi/executive-summary-the-conceptual-model-completeness-conjecture-cmcc-5490fadaa73e)

---

## Sema's twist: YAML is the SSoT, the rulebook is derived

Standard ERB projects author their CMCC instance in Airtable, sync it down to `effortless-rulebook.json`, and treat the rulebook as the SSoT.

**Sema is different**, and the GridWorks SOW (2026-05-01, §3.3) makes this contractual:

> *"The authoritative source of all schema content SHALL be the `definitions` directory on the `main` branch of the repository."*

So in sema:

- **`definitions/*.yaml`** — the authored CMCC instance (hand-edited by humans, contract-bound source of truth).
- **`effortless-rulebook.json`** — a **derived projection** of those YAMLs into CMCC form, via `yaml-to-rulebook`. Round-trip (`rulebook-to-yaml`) is currently at 96.6% (115/119 cases passing — see [`YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md`](../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md)).
- **Postgres + `vw_*` views** — derived from the rulebook (drives the Explorer UI, the snapshot builder, the public website).
- **Python runtime SDK** — currently emitted by hand-written generators in [`src/sema/tools/runtime_generation/`](../src/sema/tools/runtime_generation/) reading YAML directly. Eventually emittable from the rulebook via a `rulebook-to-python` transpiler (parallel paths to the same shape).

```
definitions/*.yaml  ←─ SSoT (per SOW §3.3)
        │
        ├─► yaml-to-rulebook  ─►  effortless-rulebook.json  (derived, this folder)
        │                                │
        │                                ├─► postgres + vw_* views
        │                                ├─► Explorer UI / public website
        │                                ├─► snapshot builder web UI
        │                                └─► (future) python / go / js SDKs
        │
        └─► src/sema/tools/runtime_generation  ─►  python SDK (jm/derived stack)
```

Both paths reach the same place. The rulebook isn't a competing SSoT — it's a **CMCC-shaped view** of the YAML that the website and snapshot tooling can ride on.

---

## How this maps to the GridWorks SOW

| SOW deliverable                                       | Mechanism                                                                                                                            |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| §3.1 public site at `schemas.electricity.works`       | Hosted-runtime instance over the rulebook + Phase 2 Explorer (already built), public read mode (auth stripped from read paths)       |
| §3.2 path-mirrored YAML (`/{kind}/{name}/{version}`)  | A `rulebook-to-yaml`/passthrough route serving each `definitions/{kind}/{name}/{version}.yaml` verbatim                              |
| §3.3 `definitions/` is canonical                      | Already true in this project. The rulebook is generated from YAML, never the other way. No mock data lives in `definitions/`.        |
| §3.4 unified build script                             | Wraps `scripts/build_registry_indexes.sh` + `yaml-to-rulebook` + `effortless build` (= postgres + views) into one PR-driven pipeline |
| §3.5 web snapshot builder                             | A CMCC view over `Types` / `EnumVersions` + a transpiler invocation (`sema snapshot prepare`/`build`) + a ZIP endpoint               |
| §3.6 knowledge transfer                               | This README + a runbook for the website + the SOW deliverable docs                                                                   |

The contract's deliverables are mostly **already-built ssotme:// machinery**, configured for sema. The remaining custom work is the snapshot-builder UI and the public-site wrapper.

---

## What's in this rulebook today

Top-level tables (current):

| Table                    | Source / origin                                              |
| ------------------------ | ------------------------------------------------------------ |
| `Owners`                 | batch 1 inferences                                           |
| `Formats` / `FormatExamples` | batch 1                                                  |
| `Enums` / `EnumValues` / `EnumVersions` | batch 2                                       |
| `Types` / `TypeVersions` / `TypeAttributes` / `TypeAxioms` / `TypeExamples` | batch 3 |
| `TypeHelpers` / `TypeHelperAttributes` | batch 4                                        |
| `Projections` / `ProjectionMappings`   | batch 5                                        |
| `EnumUpgrades` / `EnumUpgradeMappings` | batch 6                                        |
| `TypeUpgrades` / `TypeUpgradeOps`      | batch 6                                        |
| Cross-derived lifecycle predicates (`IsDraft`, `Status`, ref-staleness rollups) | batches 7a–7b |
| `AppUsers`               | magic-links allowlist                                        |

The `_meta` section holds DAG metadata, build provenance, and table-level annotations used by transpilers.

---

## Discipline

1. **Don't edit generated postgres files.** Files matching `postgres/0[0-5]-*.sql` are regenerated on every `effortless build`. Only edit `0[0-5]b-customize-*.sql` overrides if necessary.
2. **Always read from `vw_*` views, never base tables. Always write to base tables.** This is an ERB invariant.
3. **Query the rulebook efficiently.** Don't read it whole — extract `schema[]` arrays when only schema is needed; skip `data[]`. See the `effortless-query` skill.
4. **Build sandwiching.** Every `effortless build` MUST be sandwiched by commits — clean tree before, build commit immediately after, before any hand-edits. See [`../CLAUDE.md`](../CLAUDE.md) for the bright red line.
5. **The migration plan is ground truth** for structural changes — see [`../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md`](../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md).

---

## Further reading

- [`../CLAUDE.md`](../CLAUDE.md) — project-level rules and pipeline summary
- [`../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md`](../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) — full migration plan for folding the YAML and ODXML pipelines into the rulebook
- [The 5 primitives essay (Medium)](https://medium.com/effortlessapi/prove-me-wrong-every-idea-in-the-universe-melts-effortlessly-into-these-5-simple-primitives-87df9317e86e)
- [effortless-claude skill set](https://github.com/effortlessapi/effortless-claude) — the AI authoring layer that maintains CMCC instances like this one
