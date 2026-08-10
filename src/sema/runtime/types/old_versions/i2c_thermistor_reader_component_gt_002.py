from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_thermistor_channel_config import I2cThermistorChannelConfig
from sema.runtime.types.i2c_thermistor_reader_component_gt import (
    I2cThermistorReaderComponentGt,
)


class I2cThermistorReaderComponentGt002(SemaType):
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

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cThermistorReaderComponentGt002":
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

    def upgrade(self) -> I2cThermistorReaderComponentGt:
        """
        - Bus, AdcAddress, AdcReferenceVolts, SeriesResistanceKOhms dropped (facts on the board's thermistor-interface capability entry); AdcName added, naming that entry in the board record's ThermistorAdcs; DataRateSps added (the per-conversion data rate the reader writes in the ADC config word — a member of the board ADC's SupportedDataRatesSps); DeviceType dropped (TypeName is the kind; board identity lives on the board component); BoardComponentId added, anchoring the reader to its scada.board.component.gt. Context-dependent: AdcName and BoardComponentId are derived from the source layout, which the standalone component does not carry.
        """
        raise SemaType.upgrade_requires_context(
            "I2cThermistorReaderComponentGt002 cannot be upgraded to "
            "I2cThermistorReaderComponentGt without the source layout "
            "context: AdcName is derived by matching AdcAddress against the "
            "board record's ThermistorAdcs, which the standalone component "
            "does not carry."
        )
