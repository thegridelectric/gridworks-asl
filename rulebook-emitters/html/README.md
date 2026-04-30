# rulebook-to-html

Emit a single-page HTML documentation site for the entire platform.

## Inputs

[../../effortless-rulebook/effortless-rulebook.json](../../effortless-rulebook/effortless-rulebook.json) — read-only.

## Outputs (planned)

```
out/
  sema.html                    ← one self-contained HTML file (CSS + JS inlined)
```

The file is **the** documentation surface — one page covering every Format, Enum, Type, Axiom, Upgrade, and Projection in the rulebook. No multi-page nav, no external assets, no build server. Open it in a browser, ctrl-F finds anything.

This is **separate from the consuming app.** The app under design is a different artifact; this page documents the platform regardless of which app embeds it.

Sections (sketch):
- Header — rulebook snapshot identity (table counts, generated-at timestamp).
- Owners — who owns what.
- Formats — name, regex, bounds, examples, counterexamples.
- Enums — every (Name, Version) pair, default symbol, value list with descriptions.
- Types — every (Name, Version) pair, attributes table, axioms, examples.
- TypeHelpers — non-versioned reusable subtypes.
- Upgrades — TypeUpgrades + ops, Projections + mappings.
- Cross-reference index — clickable anchors between everything.

## Run

```bash
python rulebook-emitters/html/rulebook_to_html.py
# or
python rulebook-emitters/html/rulebook_to_html.py \
    --input  effortless-rulebook/effortless-rulebook.json \
    --output rulebook-emitters/html/out
```

Then `open rulebook-emitters/html/out/sema.html`.

## Status

Scaffold only. CLI summarizes the rulebook and writes a placeholder. Templating approach (Jinja2 vs stdlib) lands when codegen does.
