from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.electric_meter_component_gt import ElectricMeterComponentGt
from sema.runtime.types.old_versions.electric_meter_channel_config_000 import (
    ElectricMeterChannelConfig000,
)


class ElectricMeterComponentGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ElectricMeterChannelConfig000]
    modbus_host: str | None = None
    modbus_port: PositiveInt | None = None
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["electric.meter.component.gt"] = "electric.meter.component.gt"
    version: Literal["001"] = "001"

    def upgrade(self) -> ElectricMeterComponentGt:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "ElectricMeterComponentGt001 cannot be upgraded to "
            "ElectricMeterComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component referenced, which "
            "the standalone component does not carry."
        )
