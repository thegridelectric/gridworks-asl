from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.electric_meter_channel_config import ElectricMeterChannelConfig


class ElectricMeterComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ElectricMeterChannelConfig]
    modbus_host: str | None = None
    modbus_port: PositiveInt | None = None
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["electric.meter.component.gt"] = "electric.meter.component.gt"
    version: Literal["001"] = "001"
