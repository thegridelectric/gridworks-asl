# CLI / Derived-Code Change Report

**Window:** last 2 weeks (≈ 2026-04-29 → 2026-05-13)
**Frame of reference:** the ERB rulebook at `effortless-rulebook/effortless-rulebook.json` is **not** the SSoT of these changes. All of the churn below is on the *legacy* side of the migration plan — YAML under [definitions/](definitions/) plus the Python runtime + tooling under [src/sema/](src/sema/). The ODXML/XSLT pipeline under [code_gen/GridworksCore/](code_gen/GridworksCore/) was **not touched** in this window.

The activity falls into three buckets: (1) a major refactor of the YAML/runtime pipeline ("snapshot generation + registry governance"), (2) a steady stream of YAML vocabulary additions/edits, (3) regenerated/handwritten Python runtime + jinja templates following from (2).

---

## 1. Pipeline refactor — single biggest change

**Commit:** [87bbeef](commit) "Add snapshot generation and registry governance" (merged via PR #13, `jm/derived`)

This is the structural change underneath everything else. Highlights:

- **New CLI subcommands** under [src/sema/interfaces/cli/](src/sema/interfaces/cli/):
  - [snapshot.py](src/sema/interfaces/cli/snapshot.py) — `snapshot prepare` / `snapshot build` produce self-contained vocabulary snapshots under `output/sema`. Prepare expands a structured seed request, writes restricted `definitions/` + indexes, emits `local_names.yaml`. Build generates runtime code using an explicit package import root.
  - [runtime.py](src/sema/interfaces/cli/runtime.py) — runtime regeneration is now its own CLI verb.
  - [seed.py](src/sema/interfaces/cli/seed.py) **deleted** (149 lines) — replaced by the snapshot flow.
- **New public-registry layer.** `indexes/public_registry.yaml` is now the publishable surface. `definitions/registry.yaml` still holds draft words/versions but they're excluded from public indexes and from default runtime regeneration. New tool [build_public_registry.py](src/sema/tools/build_public_registry.py) (195 lines) drives this.
- **Custom runtime behavior moved into templates.** Axiom and upgrade Python is now generated from `runtime_generation/templates/axioms/*.py.jinja2` and `runtime_generation/templates/upgrades/*.py.jinja2`. Runtime generation **fails** if a schema declares an axiom or upgrade without a matching template — handwritten runtime logic is now explicit and reviewable.
- **Tool churn under [src/sema/tools/](src/sema/tools/):**
  - Renamed `build_seed_snapshot.py` → [build_seed_definitions.py](src/sema/tools/build_seed_definitions.py).
  - Significant rewrites of [build_seed_expanded.py](src/sema/tools/build_seed_expanded.py) (+204 lines), [runtime_generation/enums.py](src/sema/tools/runtime_generation/enums.py), [runtime_generation/formats.py](src/sema/tools/runtime_generation/formats.py), [runtime_generation/generate_runtime.py](src/sema/tools/runtime_generation/generate_runtime.py), [runtime_generation/helpers.py](src/sema/tools/runtime_generation/helpers.py).
  - Deleted: `cli_generate_runtime.py`, `generate_runtime_from_dag.py`, `rulebook_to_yaml.py`, `yaml_to_rulebook.py`, `yaml_round_trip_check.py`, `runtime_generation/imports.py`, `runtime_generation/naming.py`, `runtime_generation/schema.py`, `templates/codec.py.jinja2`, `templates/seed_request_template.yaml`.
- **Spec / lifecycle changes baked into pipeline:** active/draft status, `replaced_by` as advisory word-level metadata, primitive constraints via formats, const usage, oneOf composition, inline-object limits, default-value rules, projections, axiom clause labels.

### Follow-up commits riding on the refactor

- [c79bdac](commit) "Fixed dependencies, regenerating indexes, added axiom implementations (via Claude)" — first big batch of axiom templates and runtime regen against the new pipeline (33 files, +700 lines).
- [207edd3](commit) "Registry updates from Claude" — `definitions/registry.yaml` +319 lines.
- [4168884](commit) "YAML type definitions from Claude" — 20 new YAML type/enum files, +1135 lines.
- [1e2c0cf](commit) "add to_index, from_index to enums."
- [7c97f69](commit) "Fix for include_all_versions" in [build_seed_expanded.py](src/sema/tools/build_seed_expanded.py).
- [13e9e6a](commit) "make tests idempotent on files".
- [9d44997](commit) "Add logic template closure validation".
- [35af9e2](commit) "update registry for jinja dependency closure test".

---

## 2. YAML vocabulary changes (`definitions/`)

These are SSoT edits on the legacy side. Pre Phase-3 cutover, `definitions/*.yaml` is still authoritative.

### New types / enums introduced

- `**main.auto.state`** — promoted to versioned, starts at v001 ([f1bc986](commit), [e492122](commit)).
- `**gw1.*` SCADA state enums** — `gw1.lc.top.state`, `gw1.leaf.ally.all.tanks.state`, `gw1.leaf.ally.buffer.only.state`, `gw1.local.control.all.tanks.state`, `gw1.local.control.buffer.only.state`, `gw1.local.control.standby.top.state` ([78c01aa](commit), PR #15).
- `**heartbeat.a`** — v000 + v001, plus new `hex.char` format ([f1727a8](commit), [c79bdac](commit)).
- `**synced.readings.bundle`** v002 with sub-types for axioms ([05829df](commit), PR #14).
- `**sim.ready`, `sim.timestep**` ([239fd60](commit) WIP).
- `**log.level**` enum ([4168884](commit), descriptions in [a2c24ca](commit)).

### Notable schema edits

- `**flo.params.house0**` — versions 003 → 007 added, +2378 lines across YAML, runtime, and upgrade templates ([5af5f54](commit)).
- `**scada.params` / `ha1.params**` — `ha1.params` fields changed `str` → `const`, new `scada.params/005.yaml` ([aff743b](commit), [673edc4](commit)).
- `**new.command.tree**` — descriptions + axioms ([caafb63](commit)).
- `**weather**` dropped ("not sent by anything"), `**weather.forecast**` descriptions added ([982eb53](commit)).
- **Description-only updates:** ticklist words ([3165a75](commit)), `gridworks.event.problem`/`glitch`/`log.level` ([a2c24ca](commit)), `atn.bid`/`latest.price` ([73cdb8d](commit)).

### Vocabulary deletions (from snapshot refactor cleanup)

Driven by the new public-registry/active-vs-deprecated split, the following Python runtime modules were removed (their underlying YAML either deleted or marked non-public):
`fis_authorization_decision`, `fis_authorization_reason`, `g_node_class`, `gw0_representation_status`, `message_category`, `message_category_symbol`, `bid_recommendation`, `component_gt`, `device_type`, `fis_instance_authorization_event`, `gw0_house_address/contact/status`, `gw_channel_config`, `gw_device_type`, `market`, `node_gt`, `rco_relay_reading`, `tank_module_params`, `weather`.

---

## 3. Python runtime (`src/sema/runtime/`)

These are downstream of the YAML edits — under the new pipeline they're effectively generated, but pre-cutover they're still committed. Worth flagging because they show how much surface the YAML SSoT now drives:

- ~25 new `types/*.py` and `enums/*.py` modules (matching the new/versioned YAML above).
- ~17 new `old_versions/*.py` modules + matching `runtime_generation/templates/upgrades/*.py.jinja2` (e.g. `flo_params_house0_003_to_004` … `006_to_007`, `heartbeat_a_000_to_001`, `scada_params_004_to_005`, `ha1_params_005_to_006`).
- ~7 new axiom templates under `runtime_generation/templates/axioms/` (`atn_bid_002`, `energy_instruction_000`, `fsm_event_000`, `heating_forecast_000`, `new_command_tree_000`, `ticklist_hall_101`, `ticklist_reed_101`, `weather_forecast_000`).
- Heavy edits to [runtime/property_format.py](src/sema/runtime/property_format.py) (~442 lines reshuffled) and [runtime/enums/gw_str_enum.py](src/sema/runtime/enums/gw_str_enum.py).

---

## 4. What was *not* touched

- [code_gen/GridworksCore/](code_gen/GridworksCore/) (ODXML/XSLT) — **zero commits**. Legacy generator is dormant and on track to be deleted at Phase 6 of the migration plan.
- [effortless-rulebook/effortless-rulebook.json](effortless-rulebook/effortless-rulebook.json) — the sema-ERB SSoT — got minor edits ([32a42e2](commit) AppUsers, [518ac4b](commit) Explorer schema, [9753d74](commit) lifecycle precondition, [1db7a05](commit) mock-data tooling), but **none** of those reflect the YAML-side work above. The legacy YAML SSoT and the ERB-rulebook SSoT are still on independent tracks; nothing in this window advanced the YAML → rulebook fold-in described in [YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md](YAML-ODXML-RULEBOOK-MIGRATION-PLAN.md).

---

## Summary

The CLI / derived-code side moved decisively in the last two weeks:

1. **Pipeline:** a `seed`-based flow was replaced by a `snapshot`-based flow, with a public-registry layer separating draft from publishable vocabulary and template-driven axiom/upgrade code.
2. **YAML SSoT:** ~20 new type/enum files, several new versions on existing types, and a coordinated description/axiom pass across the catalog.
3. **Python runtime:** large regeneration consistent with (1) and (2), plus a meaningful pruning of deprecated types.
4. **ODXML/XSLT:** quiet. Migration-plan Phase 6 is still pending and unblocked-but-not-started.
5. **ERB rulebook:** untouched by any of the above. The migration plan's "fold YAML SSoT into the rulebook" step has not progressed in this window.

