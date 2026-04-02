from pydantic import ValidationError

from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.runtime.enums.old_versions.spaceheat_telemetry_name_006 import SpaceheatTelemetryName006
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.old_versions.data_channel_gt_001 import DataChannelGt001


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


def test_data_channel_gt_001_upgrade_to_002() -> None:
    old = DataChannelGt001(
        name="hp-odu-pwr",
        display_name="HP ODU Power",
        about_node_name="hp-odu",
        captured_by_node_name="primary-scada",
        telemetry_name=SpaceheatTelemetryName006.PowerW,
        terminal_asset_alias="d1.isone.me.versant.keene.peach.ta",
        in_power_metering=True,
        start_s=1736726400,
        id="123e4567-e89b-42d3-a456-426614174000",
    )

    upgraded = old.upgrade()

    assert isinstance(upgraded, DataChannelGt)
    assert upgraded.version == "002"
    assert upgraded.telemetry_name == SpaceheatTelemetryName.PowerW
    assert upgraded.quantity == Gw1Quantity.Power
    assert upgraded.in_power_metering is True
    assert upgraded.start_s == 1736726400
