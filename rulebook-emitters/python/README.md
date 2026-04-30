# rulebook-to-python

Emit Python source from the rulebook.

## Inputs

[../../effortless-rulebook/effortless-rulebook.json](../../effortless-rulebook/effortless-rulebook.json) — read-only.

## Outputs (planned)

`out/` is committed; every file carries a `# GENERATED — DO NOT EDIT` header.

```
out/
  formats/<name>.py            ← regex/length validators per Format row
  enums/<name>/<NNN>.py        ← StrEnum class per EnumVersion + value descriptions
  types/<name>/<NNN>.py        ← Pydantic model per TypeVersion + axioms in docstring
  helpers/<name>.py            ← Pydantic models for TypeHelpers (non-versioned)
  __init__.py                  ← package init exposing the public surface
```

This is **not** the same as the live runtime under [../../src/sema/runtime/](../../src/sema/runtime/), which is hand-authored today. Phase 3 of the migration plan describes cutover; until then this emitter writes to its own tree and consumers opt in.

## Run

```bash
python rulebook-emitters/python/rulebook_to_python.py
# or
python rulebook-emitters/python/rulebook_to_python.py \
    --input  effortless-rulebook/effortless-rulebook.json \
    --output rulebook-emitters/python/out
```

## Status

Scaffold only. The CLI loads the rulebook and prints a table summary. Codegen logic is the next step — see [../../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](../../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) for the schema shape this needs to traverse.
