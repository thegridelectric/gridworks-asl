# sema — next steps

> **Replaces:** [ERB-SCAFFOLD-PLAN.md (retired)](#), [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md (retired)](#), [JM_DERIVED_INTEGRATION_PLAN.md](#), [APP_PLAN.md](#), [APP_PLAN-NOTES.md](#) — all consolidated here.
>
> **Scope.** This is the live forward-looking doc. The scaffold work that *described* HEAD in the rulebook is done. What's left is closing the loop (round-trip parity, downstream emitters) and building the admin app.
>
> **Anchor rule.** [`definitions/*.yaml`](definitions/) is the contract-bound SSoT (GridWorks SOW §3.3). The rulebook is a derived projection. The architecture diagram in [README.md](README.md#architecture-the-loop) is the canonical picture; this doc is the punch list against it.

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

A web endpoint that wraps `sema snapshot prepare` / `sema snapshot build`. Per JM_DERIVED §3 the rulebook is the *catalog* (what's pickable) and `sema snapshot` is the *engine* (what builds the SDK). The UI:

- Lets a user select root types/enums/formats from the rulebook.
- Posts to a FastAPI endpoint that shells out to `sema snapshot prepare` then `sema snapshot build`.
- Returns a download URL for the generated Python package.

### C4. Edit ergonomics (Phase 5+ in APP_PLAN)

Editing surface: every field on every row writable via inline form components. The four-FK picker on TypeAttributes is the most complex single widget. Validation via `react-hook-form` + `zod` if needed.

When this lands, the loop is fully bidirectional — edit YAML OR edit through the app, both flow through the rulebook to the same end state.

---

## 4. Phase D — Deployment (SOW §3.4 / §3.6)

- [ ] **D1.** Replace the bases.effortlessapi.com magic-links auth (currently mocked for local) with the real auth wiring for production. The infra is mostly in place — see [DEPLOY.md](DEPLOY.md) and the `auth.trusted_tenants` table.
- [ ] **D2.** Deploy to Control Plane (CPLN) or equivalent. Domain TBD.
- [ ] **D3.** End-to-end smoke test against the deployed instance.

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

## 7. References

- [README.md](README.md) — architecture diagram + Sema overview.
- [CLAUDE.md](CLAUDE.md) — project rules and build discipline.
- [DEPLOY.md](DEPLOY.md) — deployment procedures.
- [rulebook-emitters/README.md](rulebook-emitters/README.md) — emitter inventory.
- The `vw_*` views in postgres — live signal of rulebook state (run `psql -d sema -c "\dv vw_*"`).
