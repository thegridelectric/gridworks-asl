from pydantic import ValidationError

from sema.runtime.enums.gw1_emission_method import Gw1EmissionMethod
from sema.runtime.types.derived_channel_gt import DerivedChannelGt
from sema.runtime.types.old_versions.derived_channel_gt_000 import DerivedChannelGt000


def test_derived_channel_gt_emission_semantics() -> None:
    try:
        DerivedChannelGt(
            id=str(__import__("uuid").uuid4()),
            name="required-energy",
            created_by_node_name="derived-generator",
            strategy="system-model",
            input_channel_names=[],
            emission_method="Periodic",
            display_name="Required Energy",
            terminal_asset_alias="d1.isone.ct.newhaven.orange1.ta",
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")


def test_derived_channel_gt_000_upgrade_to_001() -> None:
    old = DerivedChannelGt000(
        id="123e4567-e89b-42d3-a456-426614174000",
        name="usable-energy",
        created_by_node_name="derived-generator",
        strategy="layer-by-layer",
        output_unit="WattHours",
        display_name="Usable Energy Wh",
        terminal_asset_alias="d1.isone.ct.newhaven.orange1.ta",
    )

    upgraded = old.upgrade()

    assert isinstance(upgraded, DerivedChannelGt)
    assert upgraded.version == "001"
    assert upgraded.input_channel_names == []
    assert upgraded.emission_method == Gw1EmissionMethod.OnTrigger
    assert upgraded.parameters is None
    assert upgraded.output_unit == "WattHours"
