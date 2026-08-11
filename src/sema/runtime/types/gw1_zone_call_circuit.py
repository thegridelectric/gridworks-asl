from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import ZoneActuatorKind
from sema.runtime.enums import ZoneCircuitRole
from sema.runtime.enums import ZoneSetpointSource
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.gw1_zone_thermostat import Gw1ZoneThermostat


class Gw1ZoneCallCircuit(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.zone.call.circuit/000"""

    circuit_position: PositiveInt
    serves_zone: SpaceheatName
    actuator_kind: ZoneActuatorKind
    role: ZoneCircuitRole
    can_cool: bool
    setpoint_source: ZoneSetpointSource
    thermostat: Gw1ZoneThermostat
    whitewire_channel_name: SpaceheatName
    failsafe_relay_node: SpaceheatName
    ops_relay_node: SpaceheatName
    type_name: Literal["gw1.zone.call.circuit"] = "gw1.zone.call.circuit"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1ZoneCallCircuit":
        """
        Axiom 1: FloorLoopsCannotCool
        If ActuatorKind is FloorLoop, CanCool SHALL be false.
        """
        if self.actuator_kind == ZoneActuatorKind.FloorLoop and self.can_cool:
            raise ValueError(
                "Axiom 1 (FloorLoopsCannotCool) failed: ActuatorKind is "
                "FloorLoop, so CanCool SHALL be false."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "Gw1ZoneCallCircuit":
        """
        Axiom 2: ReadSetpointNeedsCommsStat
        If SetpointSource is FromThermostat, Thermostat.Kind SHALL NOT be MechanicalDial.
        """
        # Method-local: ThermostatKind is not a field enum of this type, so the
        # generator does not emit a module-level import for it.
        from sema.runtime.enums import ThermostatKind

        if (
            self.setpoint_source == ZoneSetpointSource.FromThermostat
            and self.thermostat.kind == ThermostatKind.MechanicalDial
        ):
            raise ValueError(
                "Axiom 2 (ReadSetpointNeedsCommsStat) failed: SetpointSource is "
                "FromThermostat, so Thermostat.Kind SHALL NOT be MechanicalDial."
            )
        return self
