# rulebook-to-golang

Emit Go source from the rulebook.

## Inputs

[../../effortless-rulebook/effortless-rulebook.json](../../effortless-rulebook/effortless-rulebook.json) — read-only.

## Outputs (planned)

`out/` is committed; every file carries a `// GENERATED — DO NOT EDIT` header.

```
out/
  formats/<name>.go            ← regex/length validators per Format row
  enums/<name>/<NNN>.go        ← typed string constants + value descriptions per EnumVersion
  types/<name>/<NNN>.go        ← struct + JSON tags + axioms in doc comment per TypeVersion
  helpers/<name>.go            ← structs for TypeHelpers (non-versioned)
  go.mod / go.sum              ← (later) module wiring
```

Conventions to settle when codegen lands:
- Module name (likely `github.com/electricityworks/sema-go` or similar — TBD).
- Versioned packages: `types/data_channel_gt/v002` vs flat `DataChannelGtV002`.
- How axioms ride along (godoc `// Axiom: ...` lines vs a separate `axioms.go`).

## Run

```bash
python rulebook-emitters/golang/rulebook_to_golang.py
# or
python rulebook-emitters/golang/rulebook_to_golang.py \
    --input  effortless-rulebook/effortless-rulebook.json \
    --output rulebook-emitters/golang/out
```

The emitter is a Python script even though it produces Go — same toolchain as the other emitters here, no Go required to run.

## Status

Scaffold only. CLI summarizes the rulebook and writes a placeholder.
