# rulebook-emitters

Source-code emitters that read [effortless-rulebook/effortless-rulebook.json](../effortless-rulebook/effortless-rulebook.json) and produce downstream artifacts in other languages and formats.

This directory sits **outside** [effortless-rulebook/](../effortless-rulebook/) on purpose — the rulebook is the SSoT, while the contents here are ordinary source code that consume it. They live in the same orbit as [postgres/](../postgres/), [definitions/](../definitions/), and [definitions-emitted/](../definitions-emitted/) — at the project root, runnable as scripts, generated outputs committed to git.

## Tools

| Emitter | Reads | Writes | Status |
|---|---|---|---|
| [yaml/](yaml/) | rulebook | `definitions-emitted/` — JSON-Schema YAML, round-trips with [yaml/yaml_to_rulebook.py](yaml/yaml_to_rulebook.py) | real |
| [python/](python/) | rulebook | `python/out/` — Pydantic classes for types, IntEnum/StrEnum for enums, format validators | scaffold |
| [golang/](golang/) | rulebook | `golang/out/` — Go structs and typed enum constants | scaffold |
| [html/](html/) | rulebook | `html/out/sema.html` — single-page documentation of the entire platform | scaffold |

Each emitter is a self-contained subdirectory with:
- `rulebook_to_<lang>.py` — CLI entrypoint
- `templates/` — Jinja2 (or stdlib `string.Template`) templates
- `out/` — generated artifact, committed with `# GENERATED — DO NOT EDIT` headers

## Shared

[shared/loader.py](shared/loader.py) — minimal rulebook accessors (`load_rulebook`, `by_table`, `index_by`, `group_by`). Each emitter imports from here so that table-shape changes ripple in one place.

## The yaml/ folder is the round-trip pair

Unlike the other emitter folders, `yaml/` contains both an emitter and an inject tool:

- [yaml/rulebook_to_yaml.py](yaml/rulebook_to_yaml.py) — emits `definitions-emitted/` from the rulebook
- [yaml/yaml_to_rulebook.py](yaml/yaml_to_rulebook.py) — one-shot importer: reads `definitions/*.yaml` into the rulebook
- [yaml/yaml_round_trip_check.py](yaml/yaml_round_trip_check.py) — golden test: `definitions/` ↔ `definitions-emitted/`

Both directions live together because they're a pair — the emitter is only meaningful as the inverse of the inject tool, and the round-trip test asserts they agree.

## What lives elsewhere — and why

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
