from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import GpioSenseMode
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.gw108_gpio_sensor_component_gt import Gw108GpioSensorComponentGt
from sema.runtime.types.old_versions.channel_config_000 import ChannelConfig000


class Gw108GpioSensorComponentGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/gw108.gpio.sensor.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ChannelConfig000]
    gpio_pin: PositiveInt
    sense_mode: GpioSenseMode
    send_to_derived: bool
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gw108.gpio.sensor.component.gt"] = (
        "gw108.gpio.sensor.component.gt"
    )
    version: Literal["001"] = "001"

    def upgrade(self) -> Gw108GpioSensorComponentGt:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "Gw108GpioSensorComponentGt001 cannot be upgraded to "
            "Gw108GpioSensorComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
