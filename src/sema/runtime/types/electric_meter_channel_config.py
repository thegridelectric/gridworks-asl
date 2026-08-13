from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.egauge_register_config import EgaugeRegisterConfig


class ElectricMeterChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.channel.config/000"""

    channel_name: SpaceheatName
    egauge_register_config: EgaugeRegisterConfig | None = None
    type_name: Literal["electric.meter.channel.config"] = (
        "electric.meter.channel.config"
    )
    version: Literal["000"] = "000"
