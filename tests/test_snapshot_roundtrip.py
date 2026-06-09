"""The snapshot round-trip gate (samples generation + the atn.bid guard).

Exercises the shipped ``roundtrip.py`` harness and the build-time
``snapshot_check.generate_samples`` against the in-repo runtime codec (which is
importable in-process), so we can assert both directions:

- a canonical sample round-trips cleanly (no failures), and
- a sample that does not decode/round-trip is *caught* (non-empty failures) —
  the guard that would have stopped the ``atn.bid`` restricted-snapshot bug.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.tools.runtime_generation.generate_runtime import _render_template
from sema.tools.snapshot_check import generate_samples

ROOT = Path(__file__).resolve().parents[1]
# A real type with an authored example and a known enum dependency.
SAMPLE_TYPE = "channel.readings.list.item"
SAMPLE_SCHEMA = ROOT / "definitions" / "types" / SAMPLE_TYPE / "000.yaml"


def _load_harness(tmp_path: Path):
    """Render and import the shipped harness bound to the in-repo runtime."""
    module_text = _render_template("roundtrip.py.jinja2", import_root="sema.runtime")
    module_path = tmp_path / "roundtrip_under_test.py"
    module_path.write_text(module_text)
    spec = importlib.util.spec_from_file_location("roundtrip_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the frozen dataclass resolves its module via
    # sys.modules at class-definition time.
    sys.modules["roundtrip_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _staged_definitions(tmp_path: Path) -> Path:
    defs = tmp_path / "definitions" / "types" / SAMPLE_TYPE
    defs.mkdir(parents=True)
    shutil.copy2(SAMPLE_SCHEMA, defs / "000.yaml")
    return tmp_path / "definitions"


def test_generate_samples_writes_canonical_round_trippable_sample(
    tmp_path: Path,
) -> None:
    definitions = _staged_definitions(tmp_path)
    samples_dir = tmp_path / "samples"

    coverage = generate_samples(definitions, samples_dir, default_codec)

    sample_path = samples_dir / f"{SAMPLE_TYPE}.000.json"
    assert sample_path.exists()
    assert f"{SAMPLE_TYPE}.000.json" in coverage["seeded"]
    # Canonical form leads with identity fields (model field order), not the
    # authored example's order.
    sample = json.loads(sample_path.read_text())
    assert list(sample)[:2] == ["TypeName", "Version"]
    assert (samples_dir / "README.md").exists()

    harness = _load_harness(tmp_path)
    assert harness.run_roundtrip(samples_dir) == []


def test_round_trip_gate_flags_a_broken_sample(tmp_path: Path) -> None:
    definitions = _staged_definitions(tmp_path)
    samples_dir = tmp_path / "samples"
    generate_samples(definitions, samples_dir, default_codec)
    harness = _load_harness(tmp_path)

    # A sample that no longer decodes against its schema (wrong primitive type
    # for ValueList items). Mirrors a restricted snapshot whose vocabulary no
    # longer matches the data it must carry.
    sample_path = samples_dir / f"{SAMPLE_TYPE}.000.json"
    broken = json.loads(sample_path.read_text())
    broken["ValueList"] = "not-a-list-of-ints"
    sample_path.write_text(json.dumps(broken))

    failures = harness.run_roundtrip(samples_dir)
    assert failures, "round-trip gate must catch a non-decoding sample"
    assert failures[0].sample == f"{SAMPLE_TYPE}.000.json"
