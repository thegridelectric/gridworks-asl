# Snapshot — Restricted Runtime Generation

This sub-spec covers how a Sema **snapshot** is produced: a restricted runtime
(a subset of the vocabulary plus a generated codec) baked into a consumer
package so the consumer can decode/encode Sema messages without depending on the
full registry. It defines the *guarantees a correct snapshot build provides* —
deliberately language-neutral. The reference implementation is the Python SDK
under `src/sema/tools/`; concrete tool names (formatter, type-checker, test
framework) live in those modules' docstrings, not here.

Read [primary.md](primary.md) for core principles. This spoke concerns tooling
behavior, not the vocabulary contract (formats/enums/types) in
[registry/](registry/) and [authoring/](authoring/).

## What a snapshot is

A snapshot is a vocabulary subset plus a generated codec emitted into a
consumer's package. It ships **data, not test code**: the restricted
definitions, the generated runtime, and a generated `samples/` folder. It does
NOT vendor a test suite.

## Determinism (zero-diff regen)

A second build over an unchanged registry SHALL produce **zero diff**. This
requires two things of any SDK's generator:

- **Deterministic ordering** of all generated output (imports, type ordering,
  list members) — no run-to-run reordering.
- **Canonical formatting** of generated source applied after generation, so
  whitespace/quoting cannot drift between runs.

No wall-clock data is baked into a snapshot — in particular **no build
timestamp**. Such a field is read by nothing and forces a registry diff on every
rebuild, defeating zero-diff. Provenance is instead carried by
content-meaningful registry metadata (the registry version and its
`last_updated`), copied into the snapshot, which a consumer or CI can compare
against the producing registry.

## Atomic build (a failed build is a no-op)

Because the build gates below can fail by design, a build SHALL be **atomic**:
generate into a temporary location, run every gate there, and move the result
into place **only on success**. A failing gate leaves the previous snapshot
byte-for-byte unchanged. A failed build is never a half-write.

## Generated-code gate

After generation, the emitted source SHALL be:

- **Canonically formatted** in place (safe, semantics-preserving) — the
  zero-diff win above.
- **Checked** (lint + static types). A failure here signals a **generator**
  bug — the emitted code is the generator's responsibility — and so is reported,
  and is fatal under a strict build mode. Automated fixes SHALL NOT rewrite
  generated code wholesale: that can silently strip a deliberate lazy-import
  suppression or an "unused" re-export and hide a real defect.

## Samples

For every **type** version whose schema carries an `examples:` block, the build
emits one canonical instance under `samples/`. Samples are **types only** — only
types carry `TypeName`/`Version` and are serialized between applications, so only
a type has something to round-trip; formats and enums get none.

- **Filename** follows the Sema-typed-JSON convention (dotted `TypeName`, with
  the version appended when versioned): `<type.name>.<version>.json`, or
  `<type.name>.json` for a versionless type. Old versions are included.
- **Content** is the canonical serialized form — the authored `examples:` entry
  passed through the snapshot codec (decode then re-encode): CamelCase by alias,
  absent optionals omitted, deterministic key order. These are the exact bytes
  the runtime emits over the wire, so a sample doubles as the round-trip's
  expected output and does not churn between rebuilds.
- Samples are **generated, never hand-edited** — the source of truth is the
  schema's `examples:`.
- A coverage report is written every build (`samples/README.md`): how many
  seeded type versions have a sample and which lack one, so the gap is visible
  rather than assumed-complete.

The latest version of a type need not carry an example; a **superseded** version
MUST (see [authoring/types.md](authoring/types.md) "Superseded versions"). That
mandate is what makes old-version round-trip coverage total.

## Round-trip gate

The build runs a round-trip over the freshly written samples, inside the
temporary build location, before the atomic move. For each sample:

1. **Decode at its own version → re-encode → require byte-equality with the
   sample.** Decoding is full structural validation, so a sample that decodes
   has satisfied its schema; a stable re-encode proves the restricted vocabulary
   is closed and self-consistent. This is the check that catches a vocabulary
   word missing **only** from the restricted snapshot — the class of defect that
   shipped the `atn.bid` bug, which a full-registry test could not see.
2. For a **superseded** version, additionally **decode-old → upgrade to latest →
   re-encode**, exercising the path where restricted-snapshot defects concentrate.

### Context-dependent upgrades are exempt

Some `old → new` upgrades cannot run on a standalone instance because they need
out-of-band context (e.g. the source layout that supplies node handles and ids).
Such an upgrade refuses by design with a typed, recognizable signal (the
`UpgradeRequiresContext` marker; see
[authoring/type-semantics.md](authoring/type-semantics.md) "Context-Dependent
Upgrades"). The round-trip gate recognizes that signal and treats step 2 as an
**expected pass** for that version — the sample is still required and still must
pass step 1.

## Consumer-side verification

A snapshot MAY ship a small, opt-in round-trip harness that re-runs the same
checks over `samples/` in the **consumer's** environment — useful because the
build-time gate runs in the producer's environment. It is data-plus-loader, not
a vendored test suite. If a consumer never runs it, the build-time gate remains
the floor.
