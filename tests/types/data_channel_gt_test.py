from pydantic import ValidationError

from sema.registry.types.data_channel_gt import DataChannelGt


def test_data_channel_gt_quantity_projection() -> None:
    try:
        DataChannelGt(
            name="hp-odu-pwr",
            display_name="HP ODU Power",
            about_node_name="hp-odu",
            captured_by_node_name="primary-scada",
            telemetry_name="PowerW",
            quantity="Temperature",
            terminal_asset_alias="d1.isone.me.versant.keene.peach.ta",
            id=str(__import__("uuid").uuid4()),
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
