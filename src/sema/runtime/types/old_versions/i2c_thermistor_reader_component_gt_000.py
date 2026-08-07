from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.i2c_thermistor_channel_config_000 import (
    I2cThermistorChannelConfig000,
)
from sema.runtime.types.old_versions.i2c_thermistor_reader_component_gt_001 import (
    I2cThermistorReaderComponentGt001,
)


class I2cThermistorReaderComponentGt000(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.reader.component.gt/000"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[I2cThermistorChannelConfig000]
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
    version: Literal["000"] = "000"

    def upgrade(self) -> I2cThermistorReaderComponentGt001:
        """
        Structural-only restamp of the field-emitted shape (see 000;
        gwsproto ConfigUniqueness/AddressValidity axioms deferred).
        """
        data = self.model_dump()
        data["version"] = "001"
        data["config_list"] = [c.upgrade().model_dump() for c in self.config_list]
        return I2cThermistorReaderComponentGt001.model_validate(data)
