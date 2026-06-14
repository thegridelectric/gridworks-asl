from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_thermistor_channel_config import I2cThermistorChannelConfig


class I2cThermistorReaderComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.reader.component.gt/002"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[I2cThermistorChannelConfig]
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
    version: Literal["002"] = "002"
