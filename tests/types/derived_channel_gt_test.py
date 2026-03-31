from pydantic import ValidationError

from sema.registry.types.derived_channel_gt import DerivedChannelGt


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
