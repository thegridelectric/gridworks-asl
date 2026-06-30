"""Listed type examples MUST decode against the runtime, not just be valid JSON.

Background (hardware-layout-pass-one): the suite checks type examples are valid
JSON (tests/registry/test_example_format.py) but does NOT decode them against
the runtime, so a structurally-invalid, extra-field-bearing, or axiom-violating
example for a *latest* version slips through — test_superseded_upgrades_defined
only covers superseded (non-latest) versions. The stale gw.house0.layout example
(missing heat-call DerivedChannels) is exactly such an escape.

This test closes the gap: each (type, version) listed in VALIDATED_EXAMPLES MUST
decode through the runtime codec, which enforces structural validation,
extra="forbid", and axioms.

Per the EDD loop we ADD a type here as we author or regenerate it and confirm its
example validates ("regenerate json in EDD" — see
wiki/gridworks-scada/designs/hardware-layout-pass-one/axioms.md). Missing examples
are fine: latest versions MAY omit an example (the spec makes it optional, and
non-latest versions are already required to carry one by
tests/registry/test_superseded_examples.py). This test only validates the
examples that exist for the listed types. Goal: grow this to cover every type
that carries an example.
"""

import json
from pathlib import Path

import pytest
import yaml

from sema.runtime.codec import default_codec

REPO_ROOT = Path(__file__).resolve().parents[2]

# (type_name, version) whose example(s) MUST decode against the runtime.
# Grown as each type is touched in the hardware-layout-pass-one reshape.
VALIDATED_EXAMPLES = [
    ("capture.tuning", "000"),
    # channel.config family — capture params stripped (moved to capture.tuning)
    ("ads.channel.config", "001"),
    ("dfr.config", "001"),
    ("electric.meter.channel.config", "001"),
    ("i2c.thermistor.channel.config", "002"),
    ("relay.actor.config", "004"),
    # components whose ConfigList items shed the stripped capture params
    ("ads111x.based.component.gt", "000"),
    ("dfr.component.gt", "000"),
    ("electric.meter.component.gt", "002"),
    ("gw108.vdc.relay.component.gt", "002"),
    ("i2c.multichannel.dt.relay.component.gt", "005"),
    ("i2c.thermistor.reader.component.gt", "002"),
    ("sim.relay.component.gt", "000"),
    # bare-base components that dropped their ConfigList (channel.config orphaned)
    ("gw108.gpio.sensor.component.gt", "002"),
    ("hubitat.component.gt", "000"),
    ("hubitat.poller.component.gt", "000"),
    ("pico.btu.meter.component.gt", "001"),
    ("pico.flow.module.component.gt", "001"),
    ("pico.tank.module.component.gt", "012"),
    ("sim.pico.tank.module.component.gt", "001"),
    ("sim.sensor.component.gt", "000"),
    ("web.server.component.gt", "002"),
]


@pytest.mark.parametrize(
    "type_name,version",
    VALIDATED_EXAMPLES,
    ids=[f"{t}_{v}" for t, v in VALIDATED_EXAMPLES],
)
def test_example_decodes_against_runtime(type_name: str, version: str) -> None:
    schema_path = REPO_ROOT / "definitions" / "types" / type_name / f"{version}.yaml"
    schema = yaml.safe_load(schema_path.read_text())
    examples = schema.get("examples")
    assert examples, (
        f"{type_name}/{version} is in VALIDATED_EXAMPLES but carries no example; "
        "add an example or remove it from the list."
    )
    for i, ex in enumerate(examples):
        try:
            default_codec.from_dict(json.loads(ex))
        except Exception as exc:  # noqa: BLE001 - surface the decode failure verbatim
            raise AssertionError(
                f"{type_name}/{version} examples[{i}] does not validate against "
                f"the runtime: {exc}"
            ) from exc
