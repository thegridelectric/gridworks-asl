from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatTelemetryName
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.types.gw_native_gpio_pin import GwNativeGpioPin
from sema.runtime.types.i2c_adc_config import I2cAdcConfig
from sema.runtime.types.i2c_bus import I2cBus
from sema.runtime.types.i2c_dac_config import I2cDacConfig
from sema.runtime.types.i2c_relay_config import I2cRelayConfig
from sema.runtime.types.i2c_thermistor_interface_config import (
    I2cThermistorInterfaceConfig,
)


class Gw1ScadaDeviceTypeGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.scada.device.type.gt/000"""

    device_type: PascalCase
    display_name: str | None = None
    min_poll_period_ms: PositiveInt | None = None
    bus_list: list[I2cBus] | None = None
    telemetry_name_list: list[SpaceheatTelemetryName] | None = None
    native_gpio_inputs: list[GwNativeGpioPin] | None = None
    native_gpio_outputs: list[GwNativeGpioPin] | None = None
    i2c_relays: list[I2cRelayConfig] | None = None
    ct_adc: I2cAdcConfig | None = None
    thermistor_adcs: list[I2cThermistorInterfaceConfig] | None = None
    dacs: list[I2cDacConfig] | None = None
    type_name: Literal["gw1.scada.device.type.gt"] = "gw1.scada.device.type.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1ScadaDeviceTypeGt":
        """
        Axiom 1: BusMembership
        Every I2cBus referenced by an entry in I2cRelays, CtAdc, ThermistorAdcs, or Dacs
        SHALL appear as a Name in BusList.
        """
        bus_names = {bus.name for bus in (self.bus_list or [])}
        referenced = [relay.i2c_bus for relay in (self.i2c_relays or [])]
        referenced += [adc.i2c_bus for adc in (self.thermistor_adcs or [])]
        referenced += [dac.i2c_bus for dac in (self.dacs or [])]
        if self.ct_adc is not None:
            referenced.append(self.ct_adc.i2c_bus)
        missing = sorted({bus for bus in referenced if bus not in bus_names})
        if missing:
            raise ValueError(
                "Axiom 1 (BusMembership) failed: I2cBus value(s) "
                f"{missing} are not declared in BusList."
            )
        return self
