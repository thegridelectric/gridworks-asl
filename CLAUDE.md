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

## Branching

Vocabulary work happens on a **topic branch cut from `dev`** (e.g.
`jm/<topic>`), returned to `dev` by PR — one topic per branch. There is no
long-lived vocabulary branch: with the staging tier, a word in real dev use
lands on `dev` with `status: staging` (mutable in place) and is promoted to
`published` when it freezes (see `spec/governance.md`), so nothing
accumulates on a side branch. Check `git branch --show-current` before
editing; never author on `dev` directly.

## Regen commands

After registry or schema changes:

- `scripts/build_indexes.sh` — rebuilds `indexes/` (lookup, public_registry,
  dependency_closure, reverse_dependencies, versions)
- `scripts/regenerate_runtime.py` — regenerates runtime code from schemas

## Upgrade deltas live in three coupled places

When a versioned type gains a new version, the `<a> -> <b>` change delta is
recorded **three** times — touch one, reconcile all three:

- the upgrade template body **and** docstring
  (`src/sema/tools/runtime_generation/templates/upgrades/<type_snake>_<a>_to_<b>.py.jinja2`);
- `definitions/registry.yaml` → `types.<type>.versions.<b>.summary` — the prose
  change-list (kept a mirror copy of the upgrade docstring);
- `definitions/registry.yaml` → `types.<type>.versions.<b>.direct_dependencies`
  — the machine change-list.

The docstring↔summary mirror is enforced by
`tests/registry/test_upgrade_summary_matches_template.py`. The hard rule the
upgrade *body* must satisfy: a nested sub-type whose version changes between the
outer type's `<a>` and `<b>` MUST be lifted via its own `.upgrade()`
(spec: `spec/authoring/type-semantics.md` "Nested Upgrades") — a dependency
delta in the registry with no matching lift in the body is the bug class this
coupling exists to catch.

## Adding or modifying a vocabulary word

Use the `/make-sema-word` slash command. It loads the per-word ritual
(summarize the rules for the kind you're touching, state intent, wait for
confirmation) on top of the universal MUSTs above.
