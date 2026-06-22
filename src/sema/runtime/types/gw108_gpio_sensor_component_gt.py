from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GpioSenseMode
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_config import ChannelConfig


class Gw108GpioSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw108.gpio.sensor.component.gt/002"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[ChannelConfig]
    gpio_pin: PositiveInt
    sense_mode: GpioSenseMode
    send_to_derived: bool
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gw108.gpio.sensor.component.gt"] = (
        "gw108.gpio.sensor.component.gt"
    )
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw108GpioSensorComponentGt":
        """
        Axiom 1: ChannelNameUniqueness
        Channel names SHALL be unique across the ConfigList.
        """
        channel_names = [config.channel_name for config in self.config_list]
        if len(channel_names) != len(set(channel_names)):
            raise ValueError(
                "Axiom 1 (ChannelNameUniqueness) failed: channel names must be "
                "unique across the ConfigList."
            )
        return self
