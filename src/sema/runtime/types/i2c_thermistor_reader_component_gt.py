from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_thermistor_channel_config import I2cThermistorChannelConfig


class I2cThermistorReaderComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.reader.component.gt/000"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[I2cThermistorChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    bus: SpaceheatName
    adc_address: StrictInt
    adc_reference_volts: PositiveFloat = 3.3
    series_resistance_k_ohms: PositiveFloat
    temp_calc_method: TempCalcMethod
    type_name: Literal["i2c.thermistor.reader.component.gt"] = (
        "i2c.thermistor.reader.component.gt"
    )
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cThermistorReaderComponentGt":
        """
        Axiom 1: ConfigUniquenessAndDeviceChannelConsistency
        Each ChannelName SHALL appear at most once in ConfigList. For each AdcChannel, at
        most one config in ConfigList may use Unit equal to Celcius.
        """
        seen_channel_names: set[str] = set()
        celcius_per_adc_channel: dict[object, int] = {}
        for config in self.config_list:
            if config.channel_name in seen_channel_names:
                raise ValueError(
                    f"Axiom 1 failed: channel_name {config.channel_name!r} "
                    "appears more than once in config_list."
                )
            seen_channel_names.add(config.channel_name)

            if config.unit == SpaceheatUnit.Celcius:
                celcius_per_adc_channel[config.adc_channel] = (
                    celcius_per_adc_channel.get(config.adc_channel, 0) + 1
                )
                if celcius_per_adc_channel[config.adc_channel] > 1:
                    raise ValueError(
                        f"Axiom 1 failed: adc_channel {config.adc_channel!r} has "
                        "more than one config with Unit equal to Celcius."
                    )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "I2cThermistorReaderComponentGt":
        """
        Axiom 2: AddressValidity
        AdcAddress SHALL be a valid 7-bit I2C address in the range 0 through 127.
        """
        if not 0 <= self.adc_address <= 127:
            raise ValueError(
                f"Axiom 2 failed: adc_address {self.adc_address!r} must be a 7-bit "
                "I2C address in the range 0 through 127."
            )
        return self
