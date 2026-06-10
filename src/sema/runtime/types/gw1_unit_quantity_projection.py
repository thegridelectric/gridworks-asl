from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1Quantity
from sema.runtime.enums.old_versions.gw1_unit_001 import Gw1Unit001


_PROJECTION = {
    Gw1Unit001.Unknown: Gw1Quantity.Unknown,
    Gw1Unit001.Unitless: Gw1Quantity.Unitless,
    Gw1Unit001.FahrenheitX100: Gw1Quantity.Temperature,
    Gw1Unit001.Watts: Gw1Quantity.Power,
    Gw1Unit001.WattHours: Gw1Quantity.Energy,
    Gw1Unit001.Gallons: Gw1Quantity.Volume,
    Gw1Unit001.GpmX100: Gw1Quantity.FlowRate,
    Gw1Unit001.Seconds: Gw1Quantity.Time,
    Gw1Unit001.SecondsX10: Gw1Quantity.Time,
    Gw1Unit001.Milliseconds: Gw1Quantity.Time,
}


class Gw1UnitQuantityProjection(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.unit.quantity.projection/000"""

    unit: Gw1Unit001
    quantity: Gw1Quantity
    type_name: Literal["gw1.unit.quantity.projection"] = "gw1.unit.quantity.projection"
    version: Literal["000"] = "000"

    @classmethod
    def project(cls, unit: Gw1Unit001) -> Gw1Quantity:
        expected = _PROJECTION.get(unit)
        if expected is None:
            raise ValueError(
                f"No projection defined for unit {unit!r}."
            )
        return expected

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1UnitQuantityProjection":
        """
        Axiom 1: EnumeratedProjectionMapping
        Every (Unit, Quantity) pair SHALL match the mapping declared in
        x-gridworks.projection.table. Any combination not present in the table is invalid.
        """
        expected = self.project(self.unit)
        if expected != self.quantity:
            raise ValueError(
                "Axiom 1 failed: unit and quantity do not match the enumerated projection."
            )
        return self
