from typing import Literal

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.gw1_unit import Gw1Unit


_PROJECTION = {
    Gw1Unit.Unknown: Gw1Quantity.Unknown,
    Gw1Unit.Unitless: Gw1Quantity.Unitless,
    Gw1Unit.FahrenheitX100: Gw1Quantity.Temperature,
    Gw1Unit.Watts: Gw1Quantity.Power,
    Gw1Unit.WattHours: Gw1Quantity.Energy,
    Gw1Unit.Gallons: Gw1Quantity.Volume,
    Gw1Unit.GpmX100: Gw1Quantity.FlowRate,
    Gw1Unit.Seconds: Gw1Quantity.Time,
    Gw1Unit.SecondsX10: Gw1Quantity.Time,
    Gw1Unit.Milliseconds: Gw1Quantity.Time
}


class Gw1UnitQuantityProjection(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.unit.quantity.projection/000"""

    unit: Gw1Unit
    quantity: Gw1Quantity
    type_name: Literal["gw1.unit.quantity.projection"] = "gw1.unit.quantity.projection"
    version: Literal["000"] = "000"

    @classmethod
    def project(cls, unit: Gw1Unit) -> Gw1Quantity:
        expected = _PROJECTION.get(unit)
        if expected is None:
            raise ValueError(f"No quantity projection defined for unit {unit!r}.")
        return expected

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1UnitQuantityProjection":
        expected = self.project(self.unit)
        if expected != self.quantity:
            raise ValueError(
                "Axiom 1 failed: unit and quantity do not match the enumerated projection."
            )
        return self
