# Project: sema

This is an **Effortless Rulebook (ERB)** project, with one important deviation from the standard ERB shape:

**The rulebook is the SSoT, hand-authored — there is no Airtable.**

Standard ERB flow: `Airtable → effortless-rulebook.json → postgres + codegen`.
Sema flow: `effortless-rulebook.json (hand-edited) → postgres + codegen`.

The ontology being modeled is sema's own type/enum/format/version-upgrade schema, currently scattered across two legacy pipelines (YAML under `definitions/` and ODXML/XSLT under `code_gen/GridworksCore/`). Both will be folded into the rulebook. See [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) for the full migration plan.

## Pipeline (current)

```
effortless-rulebook/effortless-rulebook.json  ← hand-edited (Claude maintains)
        │
        ├─► rulebook-to-postgres ─► postgres/*.sql ─► local "sema" DB
        │                                              │
        │                                              └─► vw_* views (computation surface)
        │
        ├─► rulebook-to-yaml (future, Phase 2) ─► definitions/*.yaml (becomes downstream artifact)
        │
        └─► rulebook-to-python (future, Phase 2) ─► src/sema/runtime/types/old_versions/*.py
```

YAML files under `definitions/` are still HEAD today. They become a downstream artifact at Phase 3 cutover.

## CRITICAL RULES

1. **The rulebook at `effortless-rulebook/effortless-rulebook.json` is the SSoT.** Hand-edit it directly (Claude does this). No Airtable layer.
2. **NEVER edit generated files** — `postgres/0[0-5]*.sql` are regenerated on every build. Only edit `0[0-5]b-*` override files if needed.
3. **Always read from `vw_*` views**, never base tables. Always WRITE to base tables.
4. **Query the rulebook efficiently** — don't read it whole. Use the `effortless-query` skill patterns: extract `schema[]` arrays, skip `data[]` when only schema is needed.
5. **Migration plan is the ground truth** — see [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) before making structural changes to the rulebook.

## Build Discipline — The Bright Red Line

Every `effortless build` MUST be sandwiched by commits:

1. **Before:** working tree clean (`git status --porcelain` empty). If dirty, ask the user before building.
2. **Run:** `effortless build`.
3. **Immediately after** — BEFORE any other code edit, scaffold, or tool invocation:
   `git add -A && git commit -m "effortless build: <reason>"`. The build commit contains **only** generated output.

This keeps git history readable: ontology changes (rulebook → SQL) never mix with hand-written code in the same commit.

## Database

- Local DB name: `sema`
- Connection: `postgresql://postgres@localhost:5432/sema`
- Reset: `cd postgres && ./init-db.sh` (drops and re-inits — `effortless build` does this automatically as a build step)

## Skills to Load

- `effortless-claude` — orchestrator
- `effortless-query` — querying the rulebook JSON
- `effortless-schema` — rulebook structure (tables, fields, formulas)
- `effortless-conventions` — naming, FK, DAG rules
- `effortless-sql` — `vw_*` view patterns
- `effortless-pipeline` — `effortless build`, transpilers, `effortless.json`
- `effortless-cli` — CLI commands

Skills NOT relevant to sema (no Airtable):
- ~~`effortless-airtable`~~, ~~`effortless-airtable-omni`~~, ~~`effortless-omni-prompt`~~ — sema has no Airtable surface
- ~~`effortless-bootstrap`~~ — sema isn't bootstrapped from raw text

## Project Layout (post-migration)

```
sema/
  effortless-rulebook/
    effortless-rulebook.json       ← SSoT (hand-edited)
  postgres/
    0[0-5]-*.sql                   ← generated, do not edit
    0[0-5]b-customize-*.sql        ← editable overrides (rare)
    init-db.sh                     ← runs as build step
  definitions/                     ← currently HEAD; becomes generated at Phase 3
  src/sema/
    tools/                         ← yaml-to-rulebook, rulebook-to-yaml, etc.
    runtime/                       ← generated Pydantic classes + old_versions/
  code_gen/GridworksCore/          ← legacy ODXML/XSLT pipeline; deleted at Phase 6
  YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md
  CLAUDE.md
```
