# sema — next steps

> **Replaces:** [ERB-SCAFFOLD-PLAN.md (retired)](#), [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md (retired)](#), [JM_DERIVED_INTEGRATION_PLAN.md](#), [APP_PLAN.md](#), [APP_PLAN-NOTES.md](#) — all consolidated here.
>
> **Scope.** This is the live forward-looking doc. The scaffold work that *described* HEAD in the rulebook is done. What's left is closing the loop (round-trip parity, downstream emitters) and building the admin app.
>
> **Anchor rule.** [`definitions/*.yaml`](definitions/) is the contract-bound SSoT (GridWorks SOW §3.3). The rulebook is a derived projection. The architecture diagram in [README.md](README.md#architecture-the-loop) is the canonical picture; this doc is the punch list against it.
>
> **Theoretical frame.** [`effortless-rulebook/effortless-rulebook.json`](effortless-rulebook/effortless-rulebook.json) is a CMCC instance — the same five-primitive (Schema / Data / Lookups / Aggregations / Calculated-Fields) structure that every effortless project uses. The build pipeline ([`effortless.json`](effortless.json) + the `effortless` CLI) is standard ssotme:// machinery. Sema's twist is that `definitions/*.yaml` is upstream of the rulebook, not Airtable — see [`effortless-rulebook/README.md`](effortless-rulebook/README.md) for the full framing.
>
> **Integration principle.** The remaining SOW work is a *wrap*, not a fork: the rulebook is the **catalog** (what's pickable, browsable), jm's existing snapshot CLI is the **engine** (what produces the ZIP), and the website/admin app is the **wrapper** around both. See §3.

---

## SOW deliverable map (GridWorks 2026-05-01)

| § | Deliverable                              | Hits in this doc                            |
| - | ---------------------------------------- | ------------------------------------------- |
| 3.1 | Public site at `schemas.electricity.works` | §4 (D1–D3) — auth-strip + CPLN domain      |
| 3.2 | Path mirror `/{kind}/{name}/{version}`     | §3 C5 (new)                                |
| 3.3 | `definitions/` on `main` is canonical      | Anchor rule above + §1 (Phase A enforces it) |
| 3.4 | PR workflow + unified build script         | §1 (A2) + §1 (A3) + §4 (D-CI)             |
| 3.5 | Web-based snapshot builder                 | §3 (C3)                                    |
| 3.6 | Knowledge transfer                         | §4 (D4 — runbook) + this doc + [`effortless-rulebook/README.md`](effortless-rulebook/README.md) |

**Definition of done (contract level):**

1. `https://schemas.electricity.works/{kind}/{name}/{version}` serves YAML byte-equivalent to `definitions/` on `main`.
2. `definitions/` on `main` contains no mock/test data; `build_registry.sh` regenerates everything else deterministically.
3. PR merge to `main` auto-deploys to the website within ~5 min.
4. Web snapshot builder produces a ZIP byte-equivalent to the CLI output for the same inputs.
5. Runbook explains every workflow above end-to-end.
6. End-to-end PR acceptance test passes.

---

## 0. State of the loop (2026-05-15)

| Edge in the loop | Tool | State |
|---|---|---|
| `definitions/` → `rulebook.json` | [`yaml_to_rulebook.py`](rulebook-emitters/yaml/yaml_to_rulebook.py) | ✅ working — 163/163 typeable YAMLs land in the rulebook |
| `rulebook.json` → Postgres | `rulebook-to-postgres` (effortless build) | ✅ working — 33 `vw_*` views; idempotent via 01b TRUNCATE pass |
| Postgres → admin app | FastAPI + React under [`app/`](app/) | ⚠️ scaffold only — see §3 |
| `rulebook.json` → `definitions-emitted/` | [`rulebook_to_yaml.py`](rulebook-emitters/yaml/rulebook_to_yaml.py) | ⚠️ ~97% parity — see §1 |
| `definitions/` ⇄ `definitions-emitted/` parity | [`yaml_round_trip_check.py`](rulebook-emitters/yaml/yaml_round_trip_check.py) | ⚠️ ~97% — last 4 failure cases unresolved |
| Rulebook → Python SDK | [`rulebook-emitters/python/`](rulebook-emitters/python/) | scaffold — not wired |
| Rulebook → Go SDK | [`rulebook-emitters/golang/`](rulebook-emitters/golang/) | scaffold — not wired |
| Rulebook → HTML docs | [`rulebook-emitters/html/`](rulebook-emitters/html/) | scaffold — not wired |
| Admin app → rulebook (edits) | not built yet | planned — §3 phase 5 onward |

The loop "closes" when round-trip parity hits 100% and the admin app can write back to the rulebook. Until then, edits flow one way: hand-edit YAML → rebuild.

---

## 1. Phase A — Close the round-trip (priority 1)

The single most important thing. Until this is done, the rulebook can't be regenerated from `definitions/` losslessly, which means we can't treat the YAML as the SSoT in any operational sense.

### A1. Identify and fix the 4 remaining round-trip cases

- [ ] Run `python rulebook-emitters/yaml/yaml_round_trip_check.py`, capture the diff list.
- [ ] For each failure, decide:
  - (a) Fix `yaml_to_rulebook.py` — preferred (the YAML is authoritative).
  - (b) Fix `rulebook_to_yaml.py` — when the rulebook's representation is correct and the emitter loses info.
  - (c) Pin the field as "derived only" — when it legitimately doesn't round-trip (e.g. computed timestamps).
- [ ] Add a `pytest` invariant so any future regression fails CI.

**Acceptance:** `yaml_round_trip_check.py` reports 119/119 cases passing.

### A2. Unified `scripts/build_registry.sh`

Replace the current ad-hoc index builders with one script that runs the whole loop in order:

```bash
# 1. Existing index builders
uv run python src/sema/tools/build_dependency_closure.py
uv run python src/sema/tools/build_lookup.py
uv run python src/sema/tools/build_reverse_dependencies.py
uv run python src/sema/tools/build_versions.py

# 2. Reflow the rulebook from YAML SSoT
uv run python rulebook-emitters/yaml/yaml_to_rulebook.py

# 3. Round-trip guard (fails the build below 100%)
uv run python rulebook-emitters/yaml/yaml_round_trip_check.py --strict

# 4. Rulebook → postgres
effortless build
```

### A3. CI invariant

GitHub Actions or local pre-commit hook that runs `build_registry.sh` on every PR. Any change to `definitions/` that breaks round-trip fails the build.

---

## 2. Phase B — Promote the Python emitter

The Python SDK is currently hand-authored under `src/sema/tools/runtime_generation/`. [`rulebook-emitters/python/rulebook_to_python.py`](rulebook-emitters/python/rulebook_to_python.py) is scaffolded but not wired. Path:

- [ ] **B1.** Get `rulebook_to_python.py` to emit the same Pydantic shape that `runtime_generation/` produces today.
- [ ] **B2.** Add a parity test: `runtime_generation/` output vs `rulebook_to_python` output on a fixed snapshot. Both must produce semantically identical Python.
- [ ] **B3.** When parity holds, flip `Emitters.Maturity = 'real'` for the python row, and migrate `runtime_generation/` callers to the new path.
- [ ] **B4.** Eventually retire `runtime_generation/`. (Not in scope for this turn — it's still the canonical Python SDK transpiler per JM_DERIVED's locked decision.)

Same general path applies to **golang** and **html** emitters once Python lands. Each gets its own parity test against whatever they're replacing (or just a smoke-test if nothing exists today).

---

## 3. Phase C — Registry Explorer admin app

The `/app/` admin tool. Stack locked: **React + TypeScript** front end, **FastAPI** back end, reading from postgres `vw_*` views, writing back to base tables.

### C1. Project scaffold

Already covered in [APP_PLAN.md §12 Phase 2](#) — keep that section as the implementation reference. The TL;DR:

- `app/api/` — FastAPI; reads `vw_*`, writes base tables. One route module per resource.
- `app/web/` — React + Vite + TypeScript; auto-generated typed client from FastAPI's OpenAPI.
- CORS for the local dev origin; OpenAPI viewable at `/docs`.

### C2. Read-only navigation (Phase 3 in APP_PLAN)

URL spine, three-pane shell, Word/Enum/Format timelines and detail pages, helper and projection views. Reads only — no editing yet.

**Cleanup task** before doing C2 work: APP_PLAN references the hallucinated calc fields `IsActive` / `IsDeprecated` / `IsRetired` / `RefIsStale` etc. throughout. Those don't exist; **use `IsPublished` / `IsDraft` instead**. See the memory `feedback-lifecycle-vocab` for the full rule.

### C3. Snapshot UI (the SOW §3.5 deliverable)

A web endpoint that wraps `sema snapshot prepare` / `sema snapshot build`. The rulebook is the **catalog** (what's pickable) and `sema snapshot` is the **engine** (what builds the SDK). The UI is the **wrapper** — it never re-implements the CLI logic, only orchestrates around it.

**Backend — [`app/api/routes/snapshot.py`](app/api/routes/snapshot.py):**

```python
class SeedSpec(BaseModel):
    versions: list[str] | None = None       # explicit version list
    include_all_versions: bool = False      # all registry-declared versions
    # absent → latest only

class SnapshotRequest(BaseModel):
    seeds: dict[str, dict[str, SeedSpec]]   # {types: {bid: {versions: ["000"]}}, enums: {...}}
    local_names: dict[str, str]             # canonical -> local class name
    package_name: str = "gjk"

GET  /api/snapshot/reserved-names   # Python keywords + builtins + snapshot helper module names
POST /api/snapshot/preview          # returns the resolved closure (no build)
POST /api/snapshot/build            # returns a ZIP stream
GET  /api/closure?type=...&enum=... # reuses src/sema/tools/build_seed_dag.py
```

The build handler shells out / imports jm's CLI (not subprocess — import `prepare`/`build` from [`src/sema/interfaces/cli/snapshot.py`](src/sema/interfaces/cli/snapshot.py)):

```python
@router.post("/snapshot/build")
async def snapshot_build(req: SnapshotRequest) -> StreamingResponse:
    with tempfile.TemporaryDirectory() as workdir:
        seed_yaml = render_seed_request_yaml(req.seeds)
        write(workdir / "seed_request.yaml", seed_yaml)
        prepare(workdir / "seed_request.yaml", workdir / "output")
        merge_local_names(workdir / "output/sema/indexes/local_names.yaml", req.local_names)
        build(workdir / "output", package_name=req.package_name)
        return zip_stream(workdir / "output/sema", filename="sema-snapshot.zip")
```

**Validation rules for `local_names`:**

- Reject Python keywords / builtins (`keyword.kwlist + dir(builtins)`).
- Reject names that collide with each other.
- Reject names that collide with the snapshot's runtime helper modules (`base`, `codec`, `property_format`).

**Frontend — [`app/web/src/routes/SnapshotBuilder.tsx`](app/web/src/routes/SnapshotBuilder.tsx):**

Three-pane shell:

1. **Seed picker** (left) — Types + Enums from rulebook with per-row "latest / all versions / explicit" controls. Reuse the existing [`Search.tsx`](app/web/src/routes/Search.tsx) picker.
2. **Closure preview** (middle) — calls `/api/snapshot/preview` after each seed change, renders the full dependency tree. Reuse the rendering pattern from [`TypeVersion.tsx`](app/web/src/routes/TypeVersion.tsx).
3. **Local names + download** (right) — per-class text inputs, live validation against `/api/snapshot/reserved-names`, big "Download ZIP" button → POST to `/api/snapshot/build`.

**Acceptance:**

- ZIP from `/api/snapshot/build` is byte-equivalent (after deterministic-ordering normalization) to running `sema snapshot prepare` → edit `local_names.yaml` → `sema snapshot build` from the same inputs. Add a golden test enforcing this.
- Anonymous browser sessions can use it end-to-end with no login (per SOW §3.1).
- Rate-limit `/api/snapshot/build` (default: 10 req/min per IP) since it's public and CPU-bound.

### C5. Path-mirrored YAML serving (SOW §3.2)

Separate from the rulebook-backed Explorer. The site MUST serve raw `definitions/*.yaml` at canonical paths so the SOW path-mirror invariant holds.

**Routes ([`app/api/routes/registry.py`](app/api/routes/registry.py)):**

```
GET /{kind}                          # kind index — all names
GET /{kind}/{name}                   # version index — latest + all versions
GET /{kind}/{name}/{version}         # HTML view (header + raw-yaml link)
GET /{kind}/{name}/{version}.yaml    # raw YAML, byte-equivalent to definitions/...
```

`{kind} ∈ {types, enums, formats, owners}`. The `.yaml` route reads directly from `definitions/{kind}/{name}/{version}.yaml` on disk — **never** from the rulebook — to honor §3.3's "definitions is authoritative" rule.

**Acceptance:** `curl https://schemas.electricity.works/types/bid/000.yaml` is byte-equivalent to the file at `definitions/types/bid/000.yaml` on the deployed commit.

### C4. Edit ergonomics (Phase 5+ in APP_PLAN)

Editing surface: every field on every row writable via inline form components. The four-FK picker on TypeAttributes is the most complex single widget. Validation via `react-hook-form` + `zod` if needed.

When this lands, the loop is fully bidirectional — edit YAML OR edit through the app, both flow through the rulebook to the same end state.

---

## 4. Phase D — Deployment (SOW §3.1 / §3.4 / §3.6)

- [ ] **D-Auth.** Strip magic-links auth from all read paths (GET routes that read schema content + the snapshot-builder routes). Keep auth ONLY on routes that mutate state — or remove mutation routes entirely from the public deployment. Audit [`app/api/auth.py`](app/api/auth.py) decorators systematically. Per SOW §3.1 the public site has no login.
- [ ] **D-CPLN.** Configure CPLN workload with public domain `schemas.electricity.works`. DNS CNAME → CPLN endpoint, cert provisioning. (Open question: who owns `electricity.works`? Need NS-record / CNAME ability.)
- [ ] **D-CI.** GitHub Action `.github/workflows/ci.yml` runs `scripts/build_registry.sh` on every PR. Fails CI if regenerated artifacts diverge from committed (`git diff --exit-code`). This is what enforces A3 at the repo level.
- [ ] **D-Deploy.** GitHub Action `.github/workflows/deploy.yml` on push to `main`: run `build_registry.sh`, build Docker image, push to CPLN via [`push-to-cpln.sh`](push-to-cpln.sh). `needs: [ci]` so deploy never fires before tests pass.
- [ ] **D-Smoke.** End-to-end smoke test against the deployed instance. Hits §3.2 path mirror, the snapshot-builder, and one full PR-merge → website-update cycle.
- [ ] **D-Runbook.** `docs/RUNBOOK.md` — adding a new type, adding a new enum, investigating a round-trip failure, deploying, rolling back, local development setup. The SOW §3.6 deliverable.

---

## 5. Cross-cutting cleanup

### 5a. Hallucinated lifecycle vocabulary

[APP_PLAN.md](APP_PLAN.md) and [APP_PLAN-NOTES.md](APP_PLAN-NOTES.md) (now retired by this doc, but their references may live in code) talk about `IsActive`, `IsDeprecated`, `IsRetired`, `RefIsStale`, `HasStaleReferences`, `is_promotable`, `word_is_retired`, `Status='active'`, `Status='deprecated'` — **none of these are real**. The actual lifecycle vocab is `Status ∈ {draft, published}` exclusively, and the only derived booleans are `IsPublished` / `IsDraft`. See memory `feedback-lifecycle-vocab` for the full rule and the "HTTP protocol" analogy that prevents regression.

Any code or doc that references the forbidden terms needs updating. Run `git grep -nE 'IsActive|IsDeprecated|IsRetired|RefIsStale|word_is_retired|is_promotable'` to find offenders.

### 5b. CLAUDE.md SSoT statement

[CLAUDE.md](CLAUDE.md) says *"The rulebook at `effortless-rulebook/effortless-rulebook.json` is the SSoT. Hand-edit it directly."* That's aspirational / post-migration framing. Until the round-trip is 100% and the rulebook can be regenerated losslessly from YAML, the YAML is the SSoT. Update CLAUDE.md to reflect current reality once Phase A1 lands.

---

## 6. Out of scope / explicitly deferred

- ODXML cleanup — covered by a separate in-flight PR; no work here.
- Airtable integration — sema has no Airtable surface and is not adding one.
- Reverse-engineering Python from the ERB beyond the existing emitter — Phase B covers the path, but only Python today.

---

## 7. Sequencing & risk

**Critical path to SOW completion:** A1 (round-trip 100%) → A2 (build script) → C3 (snapshot endpoint + UI) → C5 (path-mirrored YAML) → D-Auth/D-CPLN (deploy) → D-Smoke (e2e test). Estimated 1.5–2 weeks of single-developer flow.

| Risk                                                                 | Mitigation                                                                                  |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 4 round-trip failures need rulebook schema additions, not emitter fixes | Time-box A1 to 2 days; if blocked, mark failing fields derived-only and document why    |
| jm's `prepare`/`build` aren't importable as functions (only CLI)     | Refactor [`snapshot.py`](src/sema/interfaces/cli/snapshot.py) to expose plain functions     |
| Auth-strip leaks something not intended public                       | Audit every route before deploy; default to public-read/no-write; add visible banner        |
| Snapshot ZIPs don't match CLI output bit-for-bit                     | Golden test (C3 acceptance) — same `seed_request.yaml` → CLI output vs API output diff = ∅ |
| Deploy fires before tests complete                                   | `deploy.yml needs: [ci]`                                                                    |

---

## 8. References

- [README.md](README.md) — architecture diagram + Sema overview.
- [CLAUDE.md](CLAUDE.md) — project rules and build discipline.
- [DEPLOY.md](DEPLOY.md) — deployment procedures.
- [effortless-rulebook/README.md](effortless-rulebook/README.md) — CMCC framing, ssotme:// stack, theoretical context.
- [rulebook-emitters/README.md](rulebook-emitters/README.md) — emitter inventory.
- The `vw_*` views in postgres — live signal of rulebook state (run `psql -d sema -c "\dv vw_*"`).
- [CMCC Zenodo paper](https://zenodo.org/records/14761025) — the formal foundation behind the rulebook structure.
