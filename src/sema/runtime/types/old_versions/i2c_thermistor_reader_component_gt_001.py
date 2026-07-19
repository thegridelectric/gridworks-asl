from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.i2c_thermistor_channel_config_001 import (
    I2cThermistorChannelConfig001,
)
from sema.runtime.types.old_versions.i2c_thermistor_reader_component_gt_002 import (
    I2cThermistorReaderComponentGt002,
)


class I2cThermistorReaderComponentGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.reader.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[I2cThermistorChannelConfig001]
    display_name: str | None = None
    hw_uid: str | None = None
    bus: SpaceheatName
    adc_address: StrictInt
    adc_reference_volts: PositiveFloat
    series_resistance_k_ohms: PositiveFloat
    temp_calc_method: TempCalcMethod
    type_name: Literal["i2c.thermistor.reader.component.gt"] = (
        "i2c.thermistor.reader.component.gt"
    )
    version: Literal["001"] = "001"

    def upgrade(self) -> I2cThermistorReaderComponentGt002:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "I2cThermistorReaderComponentGt001 cannot be upgraded to "
            "I2cThermistorReaderComponentGt002 without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
