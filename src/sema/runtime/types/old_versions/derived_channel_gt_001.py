from typing import Any, Literal

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_emission_method import Gw1EmissionMethod
from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.gw1_unit import Gw1Unit
from sema.runtime.enums.old_versions.gw1_unit_000 import Gw1Unit000
from sema.runtime.property_format import (
    LeftRightDot,
    SpaceheatName,
    PositiveInt,
    UUID4Str,
)
from sema.runtime.types.derived_channel_gt import DerivedChannelGt as DerivedChannelGt002
from sema.runtime.types.gw1_unit_quantity_projection import Gw1UnitQuantityProjection
from sema.runtime.enums.gw1_unit import Gw1Unit as Gw1Unit001

class DerivedChannelGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/derived.channel.gt/001"""

    id: UUID4Str
    name: SpaceheatName
    created_by_node_name: SpaceheatName
    strategy: SpaceheatName
    input_channel_names: list[SpaceheatName]
    output_unit: Gw1Unit000 | None = None
    emission_method: Gw1EmissionMethod
    async_emit_delta: PositiveInt | None = None
    emit_period_s: PositiveInt | None = None
    parameters: dict[str, Any] | None = None
    display_name: str
    terminal_asset_alias: LeftRightDot
    type_name: Literal["derived.channel.gt"] = "derived.channel.gt"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DerivedChannelGt001":
        if self.emission_method == Gw1EmissionMethod.OnTrigger:
            if self.emit_period_s is not None or self.async_emit_delta is not None:
                raise ValueError(
                    "Axiom 1 failed: OnTrigger must not include emit_period_s or async_emit_delta."
                )
        elif self.emission_method == Gw1EmissionMethod.Periodic:
            if self.emit_period_s is None or self.async_emit_delta is not None:
                raise ValueError(
                    "Axiom 1 failed: Periodic requires emit_period_s and forbids async_emit_delta."
                )
        elif self.emission_method == Gw1EmissionMethod.AsyncAndPeriodic:
            if self.emit_period_s is None or self.async_emit_delta is None:
                raise ValueError(
                    "Axiom 1 failed: AsyncAndPeriodic requires both emit_period_s and async_emit_delta."
                )
        return self

    def upgrade(self) -> DerivedChannelGt002:
        """
        001 -> 002:
        - OutputUnit: required
        - OutputQuantity: add
        - OutputUnitQuantityConsistency axiom: add
        """
        data = self.model_dump()

        if self.output_unit is None:
            data["output_unit"] = "Unknown"
            data["output_quantity"] = Gw1Quantity.Unknown
        else:
            data["output_unit"] = self.output_unit.value
            data["output_quantity"] = Gw1UnitQuantityProjection.project(
                Gw1Unit001(self.output_unit.value)
            )

        data["version"] = "002"
        return DerivedChannelGt002.model_validate(data)
