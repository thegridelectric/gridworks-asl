from typing import Literal

from pydantic import ValidationError, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.old_versions.spaceheat_telemetry_name_006 import SpaceheatTelemetryName006
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.runtime.property_format import LeftRightDot, SpaceheatName, UTCSeconds, UUID4Str
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.spaceheat_telemetry_quantity_projection import SpaceheatTelemetryQuantityProjection


class DataChannelGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/data.channel.gt/001"""

    name: SpaceheatName
    display_name: str
    about_node_name: SpaceheatName
    captured_by_node_name: SpaceheatName
    telemetry_name: SpaceheatTelemetryName006
    terminal_asset_alias: LeftRightDot
    in_power_metering: bool | None = None
    start_s: UTCSeconds | None = None
    id: UUID4Str
    type_name: Literal["data.channel.gt"] = "data.channel.gt"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DataChannelGt001":
        if self.in_power_metering and self.telemetry_name != SpaceheatTelemetryName006.PowerW:
            raise ValueError(
                "Axiom 1 failed: telemetry_name must be PowerW when in_power_metering is true."
            )
        return self

    def upgrade(self) -> DataChannelGt:
        """001 -> 002: TelemetryName 006 -> 007, add Quantity, add TelemetryQuantityConsistency."""

        data = self.model_dump()
        upgraded_telemetry_name = SpaceheatTelemetryName[self.telemetry_name.name]
        upgraded_quantity = None
        for quantity in Gw1Quantity:
            try:
                projection = SpaceheatTelemetryQuantityProjection(
                    telemetry_name=upgraded_telemetry_name,
                    quantity=quantity,
                )
                upgraded_quantity = projection.quantity
                break
            except ValidationError:
                continue
        if upgraded_quantity is None:
            raise ValueError(
                f"No quantity projection found for telemetry_name={upgraded_telemetry_name}"
            )
        data["telemetry_name"] = upgraded_telemetry_name
        data["quantity"] = upgraded_quantity
        data["version"] = "002"
        return DataChannelGt.model_validate(data)
