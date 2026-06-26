from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.egauge_register_config import EgaugeRegisterConfig
from sema.runtime.types.electric_meter_channel_config import ElectricMeterChannelConfig


class ElectricMeterChannelConfig000(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.channel.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    egauge_register_config: EgaugeRegisterConfig | None = None
    type_name: Literal["electric.meter.channel.config"] = (
        "electric.meter.channel.config"
    )
    version: Literal["000"] = "000"

    def upgrade(self) -> ElectricMeterChannelConfig:
        """
        - Unit: drop (redundant; unit and scaling are carried by channel identity)
        - Exponent: drop (redundant; unit and scaling are carried by channel identity)
        """
        data = self.model_dump()
        del data["unit"]
        del data["exponent"]
        data["version"] = "001"
        return ElectricMeterChannelConfig.model_validate(data)
