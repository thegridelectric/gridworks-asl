# JM_DERIVED Integration Plan

**Status:** Draft v1 — 2026-05-01
**Branch context:** `ej-dev` is current; `jm/derived` is fully merged into it (last merge `b7fd5ea`, 2026-05-01).
**Contract context:** GridWorks SOW signed 2026-05-01 (§3.1 – §3.6).

---

## 0. TL;DR

There are two streams of work that ended up in `ej-dev`, both modeling the same ontology from opposite directions:

- **jm/derived stream** — `definitions/*.yaml` → hand-authored generators in [`src/sema/tools/runtime_generation/`](src/sema/tools/runtime_generation/) → Python SDK + a 2-step snapshot CLI (`prepare` / `build`) under [`src/sema/interfaces/cli/snapshot.py`](src/sema/interfaces/cli/snapshot.py).
- **ej-dev stream** — the same ontology re-expressed in [`effortless-rulebook/effortless-rulebook.json`](effortless-rulebook/effortless-rulebook.json) (a CMCC instance), driving postgres + `vw_*` views + a FastAPI/React Explorer UI under [`app/`](app/), plus a `yaml-to-rulebook` ↔ `rulebook-to-yaml` round-trip.

The GridWorks SOW pins **`definitions/*.yaml` on `main` as the SSoT (§3.3)**. So the integration is not a fork — it's a **wrap**:

```
definitions/*.yaml  ──── SSoT (contract-bound)
        │
        ├─► yaml-to-rulebook ─►  effortless-rulebook.json  (derived CMCC instance)
        │                              │
        │                              ├─► postgres + vw_*           (Explorer UI, public website)
        │                              ├─► (NEW) snapshot UI route   (SOW §3.5)
        │                              └─► (future) python/go/js SDKs (transpilers)
        │
        └─► src/sema/tools/runtime_generation ─► Python SDK
                                                   ▲
                                                   │
                                       (NEW) wrapped behind a web endpoint
                                              that the snapshot UI calls
```

The rulebook becomes the **catalog** that the website browses; jm's snapshot CLI becomes the **engine** that the snapshot-builder UI invokes server-side. Same ontology, two complementary roles.

---

## 1. Architectural decision (locked)

| Question                                         | Decision                                                                                                   |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Where is the SSoT?                               | `definitions/*.yaml` on `main`, per SOW §3.3.                                                              |
| What is the rulebook?                            | A derived CMCC projection of the YAML — regenerated on every build, never hand-edited as the SSoT.         |
| What drives the website (browse + read)?         | The rulebook (via FastAPI/Explorer over postgres + `vw_*` views).                                          |
| What drives snapshot generation?                 | jm's `sema snapshot prepare` / `sema snapshot build` CLI, invoked server-side from a new web endpoint.     |
| Where do new SDK targets (go/js) live?           | New transpilers in `rulebook-emitters/` consuming the rulebook — not new generators reading YAML directly. |
| Does jm's `runtime_generation/` stay?            | Yes. It is the Python SDK transpiler. Stays canonical until / unless `rulebook-to-python` reaches parity.  |
| Does the rulebook ever flow back into YAML?      | Only through `rulebook-to-yaml` for round-trip verification. Never as authoring.                           |

---

## 2. Current state inventory

### 2.1 jm/derived stack — Python SDK from YAML

**Location:** `src/sema/tools/runtime_generation/`, `src/sema/runtime/`, `src/sema/interfaces/cli/snapshot.py`.

| Module                                                         | Role                                                                          |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [`runtime_generation/enums.py`](src/sema/tools/runtime_generation/enums.py)               | Emits `GwStrEnum` subclasses with `to_index` / `from_index` (jm 1e2c0cf).     |
| [`runtime_generation/formats.py`](src/sema/tools/runtime_generation/formats.py)           | Emits format validators from YAML format definitions.                          |
| [`runtime_generation/types.py`](src/sema/tools/runtime_generation/types.py)               | Emits Pydantic types + per-type axiom + upgrade logic artifacts.               |
| [`runtime_generation/helpers.py`](src/sema/tools/runtime_generation/helpers.py)           | Class-name / module-name / target-path helpers (consolidated by 0ba71f0).      |
| [`runtime_generation/templates/format.py`](src/sema/tools/runtime_generation/templates/format.py) | Template strings for runtime emission.                                |
| [`runtime_generation/generate_runtime.py`](src/sema/tools/runtime_generation/generate_runtime.py) | Top-level orchestrator that walks the DAG and emits the snapshot.    |
| [`tools/build_seed_dag.py`](src/sema/tools/build_seed_dag.py)               | Computes the dependency DAG over types/enums/formats.                          |
| [`tools/build_seed_definitions.py`](src/sema/tools/build_seed_definitions.py) | Reads `definitions/` and resolves a seed request into concrete defs.          |
| [`tools/build_seed_expanded.py`](src/sema/tools/build_seed_expanded.py)     | Expands a seed request to its full closure.                                    |
| [`interfaces/cli/snapshot.py`](src/sema/interfaces/cli/snapshot.py)         | Two-step CLI: `prepare` (closure + seed_expanded.yaml + local_names.yaml) → `build` (writes Python SDK). |
| [`runtime/enums/gw_str_enum.py`](src/sema/runtime/enums/gw_str_enum.py)     | Runtime base — `to_index` / `from_index` / `default()` / `_missing_`.          |
| [`runtime/property_format.py`](src/sema/runtime/property_format.py)         | Runtime format-checking primitives.                                            |
| [`template_seed_request.yaml`](template_seed_request.yaml)                  | Top-level template for seed-request authoring.                                 |

**CLI flow today:**
```bash
uv run sema snapshot prepare template_seed_request.yaml
# → output/sema/indexes/seed_expanded.yaml
# → output/sema/indexes/local_names.yaml  (user edits this)
uv run sema snapshot build --package-name gjk
# → output/sema/{base.py,codec.py,property_format.py,enums/,types/,logic/}
```

### 2.2 ej-dev stack — Rulebook + Explorer + Postgres

**Location:** `effortless-rulebook/`, `postgres/`, `app/`, `rulebook-emitters/`, `scripts/`.

| Module                                                   | Role                                                                                        |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [`effortless-rulebook/effortless-rulebook.json`](effortless-rulebook/effortless-rulebook.json) | The CMCC instance — Owners/Formats/Enums/Types/TypeHelpers/Projections/Upgrades + cross-derived predicates. |
| [`rulebook-emitters/yaml/yaml_to_rulebook.py`](rulebook-emitters/yaml/yaml_to_rulebook.py)     | YAML → rulebook (96.6% round-trip — the load-bearing leg).                                  |
| [`rulebook-emitters/yaml/rulebook_to_yaml.py`](rulebook-emitters/yaml/rulebook_to_yaml.py)     | Rulebook → YAML (for round-trip verification).                                              |
| [`rulebook-emitters/yaml/yaml_round_trip_check.py`](rulebook-emitters/yaml/yaml_round_trip_check.py) | Round-trip pass-rate harness.                                                       |
| [`rulebook-emitters/python/`](rulebook-emitters/python/)   | Scaffold for `rulebook-to-python` transpiler (future, not wired in).                        |
| [`rulebook-emitters/golang/`, `rulebook-emitters/html/`](rulebook-emitters/) | Scaffolds for future transpilers.                                          |
| [`postgres/0[0-5]-*.sql`](postgres/)                     | Generated by `rulebook-to-postgres` transpiler. Do not edit.                                |
| [`postgres/0[0-5]b-customize-*.sql`](postgres/)          | Editable overrides (for transpiler-bug workarounds).                                        |
| [`postgres/init-db.sh`](postgres/init-db.sh)             | Runs as a build step — drops + re-inits local `sema` DB.                                    |
| [`app/api/`](app/api/)                                   | FastAPI app — auth, db, models, routes for owners/enums/formats/types/helpers/projections/upgrades/search. |
| [`app/web/`](app/web/)                                   | React + Vite Registry Explorer.                                                             |
| [`effortless.json`](effortless.json)                     | Pipeline config — `rulebook-to-postgres` → `init-db.sh`.                                    |
| [`scripts/build_registry_indexes.sh`](scripts/build_registry_indexes.sh) | The current consistency check / index builder (4 steps).                          |

### 2.3 What the SOW asks that doesn't exist yet

| SOW                                          | Gap                                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| §3.1 site at `schemas.electricity.works`     | Domain not configured; CPLN deploy targets a workload but not this DNS; auth is on by default (must be off for read paths). |
| §3.2 path mirror `/{kind}/{name}/{version}`  | No raw-YAML route. Explorer renders rulebook tables, not source YAML at canonical paths.                           |
| §3.4 unified build script                    | `build_registry_indexes.sh` only builds the four index files; doesn't run `yaml-to-rulebook` or `effortless build` or tests. |
| §3.5 snapshot builder UI                     | Doesn't exist. CLI only.                                                                                           |
| §3.6 knowledge transfer                      | Partial — [`effortless-rulebook/README.md`](effortless-rulebook/README.md) has the architectural context. Need a runbook. |

---

## 3. The integration layers

### 3.1 Catalog — what the rulebook gives the UI

The Explorer UI [`app/`](app/) already reads `vw_*` views and renders Owners / Formats / Enums / Types / Helpers / Projections / Upgrades. **No work is needed for snapshot browsing** — the existing tables already give us:

- `Types` + `TypeVersions` — the picker for "seed types"
- `Enums` + `EnumVersions` — the picker for "seed enums"
- `TypeAttributes` with `RefKind`, `EnumVersionRef`, `SubTypeVersionRef`, `HelperRef`, `RefIsStale` — enough to render the **dependency closure** when a seed is selected
- `Formats` + `FormatExamples` — for surfacing format constraints in the closure
- `TypeHelpers` + `TypeHelperAttributes` — for helper-class details

The rulebook is the **catalog**: the data behind the snapshot-builder's seed picker, closure visualizer, and validation hints.

### 3.2 Engine — what jm's CLI gives the website

jm's `snapshot prepare` / `snapshot build` is the **engine** that produces the actual ZIP. The web UI never re-implements this logic — it shells out (or calls a Python function) to:

```python
from sema.interfaces.cli.snapshot import prepare, build
# prepare(seed_request_yaml, output_dir)
# build(output_dir, package_name="gjk")
```

This isolates the contractually-relevant artifact (the ZIP) behind a single function call that already passes jm's tests.

### 3.3 The wrapper — what we have to build

A thin FastAPI route + React route that:

1. Renders a seed picker from the rulebook (catalog),
2. Lets the user assign local class names,
3. Validates them,
4. Calls the engine to produce a snapshot in a temp dir,
5. Streams a ZIP back.

That's the whole integration. Everything else is plumbing.

---

## 4. Work plan — concrete tasks

### Phase A: Foundation (must precede everything else)

#### A1. YAML round-trip parity (96.6% → 100%)

**Owner:** ej-dev. **Blocker for:** §3.3 viability.

- Run [`rulebook-emitters/yaml/yaml_round_trip_check.py`](rulebook-emitters/yaml/yaml_round_trip_check.py) and identify the 4 failing cases.
- For each failure, decide:
  - (a) Fix `yaml-to-rulebook` (preferred — preserve YAML SSoT).
  - (b) Fix `rulebook-to-yaml`.
  - (c) Pin the rulebook field to be derived-only (don't expect round-trip).
- Add a `pytest` invariant: round-trip must be 100% on every build.

**Acceptance:** `yaml_round_trip_check.py` reports 119/119 cases passing.

**Risk if skipped:** If the rulebook can't be regenerated cleanly from `definitions/*.yaml`, the SOW §3.3 invariant ("definitions on main is authoritative") breaks the moment the rulebook is touched.

#### A2. Unified build script — `scripts/build_registry.sh`

**Owner:** ej-dev. **Blocker for:** §3.4.

Replace [`scripts/build_registry_indexes.sh`](scripts/build_registry_indexes.sh) with a script that does **everything** the SOW asks:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# 1. Existing index builders (preserve current behavior)
uv run python src/sema/tools/build_dependency_closure.py
uv run python src/sema/tools/build_lookup.py
uv run python src/sema/tools/build_reverse_dependencies.py
uv run python src/sema/tools/build_versions.py

# 2. Regenerate the rulebook from YAML (NEW — replaces hand-editing)
uv run python rulebook-emitters/yaml/yaml_to_rulebook.py \
    --in definitions/ \
    --out effortless-rulebook/effortless-rulebook.json

# 3. Round-trip parity check (fails the build if < 100%)
uv run python rulebook-emitters/yaml/yaml_round_trip_check.py --strict

# 4. Effortless build (rulebook → postgres + views)
effortless build

# 5. Tests
uv run pytest tests/ -x

echo "build_registry.sh: OK"
```

**Wire it into:** the GitHub Action that runs on `main` merges (Phase D).

**Acceptance:** A no-op rerun on a clean tree produces zero diff. A YAML edit produces a deterministic rulebook diff + zero `definitions/` diff.

#### A3. Pin the build sandwich invariant in CI

**Owner:** ej-dev. **Blocker for:** ongoing project sanity.

- CI step that fails if `effortless build` artifacts (postgres SQL, rulebook JSON) are out of sync with `definitions/*.yaml`.
- This enforces the bright-red-line rule from [`CLAUDE.md`](CLAUDE.md) at the repo level.

**Acceptance:** A PR that edits YAML without rebuilding fails CI with a clear message.

---

### Phase B: Public website (SOW §3.1, §3.2)

#### B1. Public-read mode

**Owner:** ej-dev. **Depends on:** A1, A2.

- Strip magic-links auth from all GET routes that read schema content.
- Keep auth only on routes that mutate state (or remove mutation routes entirely from the public deployment).
- Audit [`app/api/auth.py`](app/api/auth.py) and route decorators.

**Acceptance:** Anonymous browser session can load every Explorer page and download any snapshot. No 401s.

#### B2. Path-mirrored YAML routes (§3.2)

**Owner:** ej-dev.

Add a route group under [`app/api/routes/`](app/api/routes/):

```python
# app/api/routes/registry.py
GET  /{kind}/{name}/{version}              # HTML view + raw-yaml link
GET  /{kind}/{name}/{version}.yaml         # raw YAML, served from definitions/
GET  /{kind}/{name}                        # version index (latest + all)
GET  /{kind}                               # kind index (all names)
```

`{kind}` ∈ `{types, enums, formats, owners}`. The route reads directly from `definitions/{kind}/{name}/{version}.yaml` on disk — **not** from the rulebook — to honor §3.3.

**Acceptance:** `curl https://schemas.electricity.works/types/bid/000.yaml` returns the exact bytes of `definitions/types/bid/000.yaml`.

#### B3. CPLN deploy → `schemas.electricity.works`

**Owner:** ej-dev. **Depends on:** B1, B2.

- Configure CPLN workload with public domain `schemas.electricity.works`.
- DNS: CNAME `schemas.electricity.works` → CPLN endpoint.
- Confirm cert provisioning.

**Acceptance:** TLS valid, anonymous access works, Lighthouse accessibility ≥ 90.

---

### Phase C: Snapshot builder UI (SOW §3.5) — the long pole

#### C1. Backend endpoint — `POST /api/snapshot/build`

**Owner:** ej-dev. **Depends on:** A2.

Add [`app/api/routes/snapshot.py`](app/api/routes/snapshot.py):

```python
class SnapshotRequest(BaseModel):
    seeds: dict[str, dict[str, SeedSpec]]   # {types: {bid: {versions: ["000"]}}, enums: {...}}
    local_names: dict[str, str]             # canonical -> local class name
    package_name: str = "gjk"

class SeedSpec(BaseModel):
    versions: list[str] | None = None       # explicit versions
    include_all_versions: bool = False      # all registry-declared versions
    # absent → latest only

POST /api/snapshot/preview        # returns the closure (no build)
POST /api/snapshot/build          # returns a ZIP stream
GET  /api/snapshot/reserved-names # for client-side validation hints
```

**Implementation:**

```python
# app/api/routes/snapshot.py (sketch)
@router.post("/snapshot/build")
async def snapshot_build(req: SnapshotRequest) -> StreamingResponse:
    with tempfile.TemporaryDirectory() as workdir:
        seed_yaml = render_seed_request_yaml(req.seeds)
        write(workdir / "seed_request.yaml", seed_yaml)

        # call jm's CLI as a Python function (NOT a subprocess —
        # importable from sema.interfaces.cli.snapshot)
        prepare(seed_request_path=workdir / "seed_request.yaml",
                output_dir=workdir / "output")

        # apply local_names from the request (overrides the empty file
        # that prepare just wrote)
        merge_local_names(workdir / "output/sema/indexes/local_names.yaml",
                          req.local_names)

        build(output_dir=workdir / "output",
              package_name=req.package_name)

        zip_bytes = zip_directory(workdir / "output/sema")
    return StreamingResponse(io.BytesIO(zip_bytes),
                             media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=sema-snapshot.zip"})
```

**Validation:**

- Reject `local_names` that match Python keywords / built-ins (`get_python_reserved()`).
- Reject `local_names` that collide with each other.
- Reject `local_names` that collide with names already in the snapshot's runtime helpers (`base.py`, `codec.py`, etc.).

**Acceptance:** ZIP from `/api/snapshot/build` is byte-equivalent to running `sema snapshot prepare` + edit + `sema snapshot build` from the same inputs.

#### C2. Frontend — `/snapshot-builder` route

**Owner:** ej-dev. **Depends on:** C1.

Add [`app/web/src/routes/SnapshotBuilder.tsx`](app/web/src/routes/SnapshotBuilder.tsx):

**UI flow (3 panes):**

1. **Seed picker** — left pane, lists Types + Enums from the rulebook. Each row supports:
   - "latest only" (default)
   - "all versions"
   - "explicit versions" (multi-select chips for available `TypeVersions` / `EnumVersions`).
2. **Closure preview** — middle pane, calls `/api/snapshot/preview` after each seed change. Shows the full transitive closure as a tree, highlighting added/removed nodes vs the previous selection.
3. **Local names + download** — right pane:
   - Per-class text input, defaulted to the canonical name in PascalCase.
   - Live validation against `/api/snapshot/reserved-names`.
   - Big "Download ZIP" button that POSTs to `/api/snapshot/build`.

**Reuse from existing routes:** [`Search.tsx`](app/web/src/routes/Search.tsx) for the picker, [`TypeVersion.tsx`](app/web/src/routes/TypeVersion.tsx) for the closure rendering pattern.

**Acceptance:**
- A user can click through Type + Enum selection → closure preview updates → assign local names → download a ZIP that opens cleanly and `python -c "from gjk.sema.types.<x> import ..."` succeeds.
- The ZIP byte-matches the CLI output for the same inputs.

#### C3. Closure visualization helper

**Owner:** ej-dev. **Depends on:** existing rulebook.

Add [`app/api/routes/closure.py`](app/api/routes/closure.py):

```python
GET /api/closure?type=bid:000&type=layout.lite:011
# returns { types: [...], enums: [...], formats: [...], helpers: [...] }
```

Reuses [`src/sema/tools/build_seed_dag.py`](src/sema/tools/build_seed_dag.py) — same DAG that powers `snapshot prepare`. Server-side, so no logic duplication.

**Acceptance:** `/api/closure` for a known seed returns exactly the same closure that `snapshot prepare` writes to `seed_expanded.yaml`.

---

### Phase D: PR-driven workflow + auto-deploy (SOW §3.4)

#### D1. GitHub Action — `.github/workflows/ci.yml`

**Owner:** ej-dev. **Depends on:** A2, A3.

```yaml
name: CI
on: [pull_request, push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install uv
      - run: ./scripts/build_registry.sh
      - name: Diff check (regenerated artifacts must match committed)
        run: git diff --exit-code
```

**Acceptance:** Editing `definitions/*.yaml` without rerunning `build_registry.sh` fails CI with a clear "regenerated artifacts out of sync" error.

#### D2. GitHub Action — `.github/workflows/deploy.yml`

**Owner:** ej-dev. **Depends on:** B3, D1.

On push to `main`:
1. Run `build_registry.sh`.
2. Build Docker image.
3. Push to CPLN via [`push-to-cpln.sh`](push-to-cpln.sh).

**Acceptance:** A merged PR appears at `schemas.electricity.works` within ~5 min, no manual steps.

---

### Phase E: Knowledge transfer (SOW §3.6)

#### E1. Runbook — `docs/RUNBOOK.md`

**Owner:** ej-dev.

Cover:
1. **Adding a new type** — edit `definitions/types/{name}/{version}.yaml`, run `build_registry.sh`, commit, PR.
2. **Adding a new enum** — same flow.
3. **Investigating a round-trip failure** — run the check script, narrow the diff, decide a/b/c per A1.
4. **Deploying** — what triggers it, how to roll back.
5. **Local development** — `init-db.sh`, `start.sh`, dev server URLs.
6. **The five primitives** — how to read [`effortless-rulebook/README.md`](effortless-rulebook/README.md) for the architectural framing.

**Acceptance:** A new GridWorks engineer can add a type via PR end-to-end without asking for help.

#### E2. End-to-end acceptance test (per SOW)

**Owner:** ej-dev.

- Open a PR that adds a new type to `definitions/types/test_acceptance/000.yaml`.
- CI passes.
- Merge to `main`.
- Confirm `https://schemas.electricity.works/types/test_acceptance/000` serves the new YAML within 5 min.
- Confirm the snapshot builder UI can include `test_acceptance:000` in a closure.
- Roll back the test type with a follow-up PR.

**Acceptance:** All three SOW acceptance criteria pass cleanly.

---

## 5. Sequencing

```
A1 round-trip 100% ──┐
                     ├─► A2 build script ──► A3 CI invariant ──► D1 PR CI
                     │                                              │
                     │                                              │
B1 strip auth ───────┤                                              │
B2 path mirror ──────┼─► B3 CPLN domain ─────────────────────────► D2 deploy ─► E2 e2e test
                     │
C3 closure API ──────┤
                     ├─► C1 snapshot endpoint ─► C2 snapshot UI ────►
                     │
                     E1 runbook (parallel, last week)
```

**Critical path:** A1 → A2 → C1 → C2 → E2.

**Estimated effort:** 1.5–2 weeks for a single developer working in flow. The long pole is C2 (snapshot UI). A1 may surprise — if the 4 failing round-trip cases need rulebook schema changes, that's another inference batch.

---

## 6. Risks and mitigations

| Risk                                                                                          | Likelihood | Mitigation                                                                                            |
| --------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
| Round-trip parity (A1) requires rulebook schema additions, not just emitter fixes.            | Medium     | Time-box A1 to 2 days; if blocked, designate the failing fields as derived-only and document why.    |
| jm's `snapshot prepare`/`build` aren't cleanly importable as Python functions (only CLI entry). | Medium     | If needed, refactor `snapshot.py` to expose `prepare(...)` / `build(...)` as plain functions.        |
| Rulebook + YAML drift during the build.                                                       | Low (after A3) | The CI diff-check guarantees they match.                                                          |
| Auth strip leaks something not intended to be public.                                          | Medium     | Audit every route before deploy. Default to "public-read, no-write" and add a banner.                 |
| Snapshot ZIPs don't match CLI output bit-for-bit.                                              | Medium     | Add a golden test: same `seed_request.yaml` → CLI output and API output diff = empty.                |
| Deploy-on-merge fires before tests complete.                                                   | Low        | `deploy.yml` `needs: [ci]`.                                                                           |
| jm changes `runtime_generation/` and breaks the API endpoint.                                  | Low        | The endpoint imports `prepare` / `build` — same surface jm's CLI uses, so same blast radius.          |

---

## 7. What this plan *doesn't* do (intentionally)

- **Does not migrate the SSoT to the rulebook.** SOW §3.3 forbids this.
- **Does not replace `runtime_generation/`** with a `rulebook-to-python` transpiler. That's a future project — stays in [`rulebook-emitters/python/`](rulebook-emitters/python/) as scaffold until the rulebook + YAML reach 100% parity AND someone has the appetite.
- **Does not add new SDK languages.** Go and JS transpilers are scaffolded but out of scope for this contract.
- **Does not delete the legacy ODXML pipeline.** Per [`YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md`](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md), that's Phase 6 work.
- **Does not bootstrap a new authoring UI for YAML.** Authoring stays in editor + PR.

---

## 8. Definition of done (contract-level)

The contract is satisfied when:

1. ✅ `https://schemas.electricity.works/{kind}/{name}/{version}` serves YAML matching `definitions/` on `main` (§3.1, §3.2).
2. ✅ `definitions/` on `main` contains no mock/test data; `build_registry.sh` regenerates everything else (§3.3, §3.4).
3. ✅ A PR that edits YAML auto-deploys to the website on merge (§3.4).
4. ✅ The web snapshot builder produces a ZIP that matches the CLI output (§3.5).
5. ✅ [`docs/RUNBOOK.md`](docs/RUNBOOK.md) explains every workflow above (§3.6).
6. ✅ The end-to-end test in §E2 passes.

---

## 9. Open questions (need GridWorks input)

1. **Domain ownership** — who owns `electricity.works`? Need NS records / CNAME ability for `schemas.electricity.works`.
2. **Snapshot ZIP includes `logic/axioms/` and `logic/upgrades/`** — these are jm's emitted artifacts. Confirm the contract reading: §3.5 says "definitions, indexes, and the runtime python for the snapshot." Runtime python = SDK + axioms + upgrades, yes? *(Probable yes — jm's CLI already produces this.)*
3. **Local-names reserved list** — beyond Python keywords and built-ins, do we want to reserve names matching the snapshot's own helper modules (`base`, `codec`, `property_format`)? *(Defaulting to yes.)*
4. **Authentication on the snapshot build endpoint** — §3.1 says no login for read or for downloads. So `/api/snapshot/build` is public. Rate-limit it? *(Default: yes, IP-based, e.g. 10/min.)*
5. **Is anyone going to author rulebook fields directly?** If yes, we need a "no-edit" guard on the rulebook JSON. If no (which is the read of §3.3), we can mark it as a generated artifact and skip the guard.

---

## 10. References

- **Project docs**
  - [`CLAUDE.md`](CLAUDE.md) — project rules, build sandwich
  - [`effortless-rulebook/README.md`](effortless-rulebook/README.md) — CMCC framing, SOW mapping
  - [`YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md`](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md) — broader migration context
  - [`APP_PLAN.md`](APP_PLAN.md) — Explorer app plan
  - [`DEPLOY.md`](DEPLOY.md) — current deploy notes
- **External**
  - [CMCC Zenodo paper](https://zenodo.org/records/14761025)
  - [SSoTme org on GitHub](https://github.com/SSoTme)
  - [Effortless ecosystem](https://github.com/effortlessapi)
