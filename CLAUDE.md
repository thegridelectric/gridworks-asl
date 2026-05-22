
You are operating under Sema constraints.

You MUST read and follow:

- Coding/sema/docs/sema-specification.md
- Coding/for_codex/sema_llm_alignment.txt

Do not proceed until you have read both.

First, summarize:
1. Core Sema rules for types, enums, formats
2. Versioning rules
3. Dependency rules

Notes on making new yaml from run-time behavior:
  - PositiveInt in SCADA -> use positive.int property format (which does not coerce and is actually strict)

Notes on making into pydantic:
  - json int -> pydantic StrictInt


Then proceed.

All changes to sema sub-folders or the sema repository MUST:

- Preserve TypeName and Version semantics
- Use CamelCase for all serialized fields
- Treat formats as immutable
- Ensure enums are additive only
- Bump type versions when required by the specification
- Maintain correct dependency declarations (direct vs all)
- Not modify historical versions
- Pass pytest and registry validation

If validation fails, fix and retry until green.

Please ask me for a Task Prompt before starting


When implementing version upgrades:

DO NOT manually reconstruct objects field-by-field
MUST use:
model_dump()
modify only changed fields
model_validate() into the next version
Upgrades MUST be:
minimal
schema-preserving
forward-compatible
Nested SemaTypes MUST be upgraded recursively via .upgrade()


