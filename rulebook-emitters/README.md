# rulebook-emitters

Source-code emitters that read [effortless-rulebook/effortless-rulebook.json](../effortless-rulebook/effortless-rulebook.json) and produce downstream artifacts in other languages and formats.

This directory sits **outside** [effortless-rulebook/](../effortless-rulebook/) on purpose — the rulebook is the SSoT, while the contents here are ordinary source code that consume it. They live in the same orbit as [postgres/](../postgres/), [definitions/](../definitions/), and [definitions-emitted/](../definitions-emitted/) — at the project root, runnable as scripts, generated outputs committed to git.

## Tools

| Emitter | Reads | Writes | Status |
|---|---|---|---|
| [python/](python/) | rulebook | `python/out/` — Pydantic classes for types, IntEnum/StrEnum for enums, format validators | scaffold |
| [golang/](golang/) | rulebook | `golang/out/` — Go structs and typed enum constants | scaffold |
| [html/](html/) | rulebook | `html/out/sema.html` — single-page documentation of the entire platform | scaffold |

Each emitter is a self-contained subdirectory with:
- `rulebook_to_<lang>.py` — CLI entrypoint
- `templates/` — Jinja2 (or stdlib `string.Template`) templates
- `out/` — generated artifact, committed with `# GENERATED — DO NOT EDIT` headers

## Shared

[shared/loader.py](shared/loader.py) — minimal rulebook accessors (`load_rulebook`, `by_table`, `index_by`, `group_by`). Each emitter imports from here so that table-shape changes ripple in one place.

## What lives elsewhere — and why

The YAML round-trip emitters predate this directory and stay in their original home:

- [src/sema/tools/rulebook_to_yaml.py](../src/sema/tools/rulebook_to_yaml.py) — emits `definitions-emitted/`
- [src/sema/tools/yaml_to_rulebook.py](../src/sema/tools/yaml_to_rulebook.py) — one-shot importer

They may move under `rulebook-emitters/yaml/` once the new emitters here stabilize. Until then, they stay put — the goal is a new home for **new** emitters, not a parallel mineshaft.

The legacy ODXML/XSLT pipeline under [code_gen/GridworksCore/](../code_gen/GridworksCore/) is not consumed here; it's slated for decommission per [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](../YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) Phase 6.

## Running an emitter

Each emitter takes the same two flags:

```bash
python rulebook-emitters/python/rulebook_to_python.py \
    --input  effortless-rulebook/effortless-rulebook.json \
    --output rulebook-emitters/python/out
```

Defaults are wired so a bare invocation also works:

```bash
python rulebook-emitters/python/rulebook_to_python.py
```

## Adding a new emitter

1. Create `rulebook-emitters/<name>/` with `README.md`, `rulebook_to_<name>.py`, `templates/`, `out/`.
2. Import `load_rulebook`, `by_table`, etc. from [shared/loader.py](shared/loader.py).
3. Follow the CLI shape of the existing emitters (`--input` / `--output` with sensible defaults).
4. Generated output gets a `# GENERATED — DO NOT EDIT` header (or language equivalent).
5. Add a row to the table above.

## Build discipline

Per [CLAUDE.md](../CLAUDE.md), every `effortless build` is sandwiched by commits. Emitters here are **not** part of `effortless build` today — they're invoked manually. If/when an emitter joins the build pipeline (as a transpiler in [effortless.json](../effortless.json)), the same sandwich rule applies: commit before, build, commit generated output as a standalone commit.
