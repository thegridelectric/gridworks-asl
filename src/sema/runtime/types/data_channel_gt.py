import uuid
from typing import Literal

from pydantic import ValidationError, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.runtime.property_format import LeftRightDot, SpaceheatName, UTCSeconds, UUID4Str
from sema.runtime.types.spaceheat_telemetry_quantity_projection import SpaceheatTelemetryQuantityProjection


class DataChannelGt(SemaType):
    """Sema: https://schemas.electricity.works/types/data.channel.gt/002"""

    name: SpaceheatName
    display_name: str
    about_node_name: SpaceheatName
    captured_by_node_name: SpaceheatName
    telemetry_name: SpaceheatTelemetryName
    quantity: Gw1Quantity
    terminal_asset_alias: LeftRightDot
    in_power_metering: bool | None = None
    start_s: UTCSeconds | None = None
    id: UUID4Str
    type_name: Literal["data.channel.gt"] = "data.channel.gt"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DataChannelGt":
        if self.in_power_metering and self.telemetry_name != SpaceheatTelemetryName.PowerW:
            raise ValueError(
                "Axiom 1 failed: telemetry_name must be PowerW when in_power_metering is true."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "DataChannelGt":
        try:
            SpaceheatTelemetryQuantityProjection(
                telemetry_name=self.telemetry_name,
                quantity=self.quantity,
            )
        except ValidationError as e:
            raise ValueError(
                "Axiom 2 failed: quantity is inconsistent with telemetry_name."
            ) from e
        return self
