from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import GpioSenseMode
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str


class GpioSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gpio.sensor.component.gt/000"""

    component_id: UUID4Str
    board_component_id: UUID4Str
    gpio_name: PascalCase
    sense_mode: GpioSenseMode
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gpio.sensor.component.gt"] = "gpio.sensor.component.gt"
    version: Literal["000"] = "000"
