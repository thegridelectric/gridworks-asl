from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatTelemetryName
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.types.gw_native_gpio_pin import GwNativeGpioPin
from sema.runtime.types.i2c_bus import I2cBus
from sema.runtime.types.i2c_ct_interface_capability import I2cCtInterfaceCapability
from sema.runtime.types.i2c_dac_capability import I2cDacCapability
from sema.runtime.types.i2c_expander import I2cExpander
from sema.runtime.types.i2c_relay_capability import I2cRelayCapability
from sema.runtime.types.i2c_thermistor_interface_capability import (
    I2cThermistorInterfaceCapability,
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
    expanders: list[I2cExpander] | None = None
    i2c_relays: list[I2cRelayCapability] | None = None
    ct_adc: I2cCtInterfaceCapability | None = None
    thermistor_adcs: list[I2cThermistorInterfaceCapability] | None = None
    dacs: list[I2cDacCapability] | None = None
    type_name: Literal["gw1.scada.device.type.gt"] = "gw1.scada.device.type.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1ScadaDeviceTypeGt":
        """
        Axiom 1: BusMembership
        Every I2cBus referenced by an entry in Expanders, CtAdc, ThermistorAdcs,
        or Dacs SHALL appear as a Name in BusList.
        """
        bus_names = {bus.name for bus in (self.bus_list or [])}
        referenced = [expander.i2c_bus for expander in (self.expanders or [])]
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

    @model_validator(mode="after")
    def check_axiom_2(self) -> "Gw1ScadaDeviceTypeGt":
        """
        Axiom 2: ExpanderMembership
        Every ExpanderIdx referenced by an entry in I2cRelays SHALL appear as an
        ExpanderIdx in Expanders.
        """
        expander_idxs = {e.expander_idx for e in (self.expanders or [])}
        missing = sorted(
            {
                relay.expander_idx
                for relay in (self.i2c_relays or [])
                if relay.expander_idx not in expander_idxs
            }
        )
        if missing:
            raise ValueError(
                "Axiom 2 (ExpanderMembership) failed: ExpanderIdx value(s) "
                f"{missing} are not declared in Expanders."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "Gw1ScadaDeviceTypeGt":
        """
        Axiom 3: BoardIdentifierUniqueness
        The board's silk-screen namespace is one namespace: the union of every
        RelayName in I2cRelays, the CtAdc Name, every Name in ThermistorAdcs,
        every DacName in Dacs, and every Name in NativeGpioInputs and
        NativeGpioOutputs SHALL contain no duplicates within the record.
        """
        names = [r.relay_name for r in (self.i2c_relays or [])]
        if self.ct_adc is not None:
            names.append(self.ct_adc.name)
        names += [a.name for a in (self.thermistor_adcs or [])]
        names += [d.dac_name for d in (self.dacs or [])]
        names += [p.name for p in (self.native_gpio_inputs or [])]
        names += [p.name for p in (self.native_gpio_outputs or [])]
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise ValueError(
                "Axiom 3 (BoardIdentifierUniqueness) failed: duplicate board "
                f"identifier name(s) {dupes}."
            )
        return self
