from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import GpioSenseMode
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str


class Gw108GpioSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw108.gpio.sensor.component.gt/002"""

    component_id: UUID4Str
    device_type: PascalCase
    gpio_pin: PositiveInt
    sense_mode: GpioSenseMode
    send_to_derived: bool
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gw108.gpio.sensor.component.gt"] = (
        "gw108.gpio.sensor.component.gt"
    )
    version: Literal["002"] = "002"
