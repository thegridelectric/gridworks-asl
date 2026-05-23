You are operating under Sema constraints.

You MUST read and follow `spec/primary.md` before proceeding
(plus the relevant spokes under `spec/registry/` and
`spec/authoring/` for the kind of work you are doing). Paths in
this file are relative to the sema repo root.

The previous monolithic spec is preserved as `spec/orig-spec.md` for
reference during the transition.

Please ask the user for a Task Prompt before starting.

## Universal MUSTs

All changes to sema sub-folders or the sema repository MUST:

- Preserve `TypeName` and `Version` semantics
- Use CamelCase for all serialized fields
- Treat formats as immutable
- Ensure enums are additive only
- Bump type versions when required by the specification
- Maintain correct dependency declarations (direct vs all)
- Not modify historical versions
- Pass `pytest` and registry validation

If validation fails, fix and retry until green.

## Regen commands

After registry or schema changes:

- `scripts/build_indexes.sh` — rebuilds `indexes/` (lookup, public_registry,
  dependency_closure, reverse_dependencies, versions)
- `scripts/regenerate_runtime.py` — regenerates runtime code from schemas

## Adding or modifying a vocabulary word

Use the `/make-sema-word` slash command. It loads the per-word ritual
(summarize the rules for the kind you're touching, state intent, wait for
confirmation) on top of the universal MUSTs above.
