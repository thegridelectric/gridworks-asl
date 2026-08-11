from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import ThermostatKind
from sema.runtime.property_format import UUID4Str


class Gw1ZoneThermostat(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.zone.thermostat/000"""

    kind: ThermostatKind
    component_id: UUID4Str | None = None
    type_name: Literal["gw1.zone.thermostat"] = "gw1.zone.thermostat"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1ZoneThermostat":
        """
        Axiom 1: NoComponentOnDumbStat
        If Kind is MechanicalDial, ComponentId SHALL be absent.
        """
        if self.kind == ThermostatKind.MechanicalDial and self.component_id is not None:
            raise ValueError(
                "Axiom 1 (NoComponentOnDumbStat) failed: Kind is MechanicalDial, "
                f"so ComponentId SHALL be absent; got {self.component_id}."
            )
        return self
