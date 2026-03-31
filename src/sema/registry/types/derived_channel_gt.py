from typing import Any, Literal

from pydantic import PositiveInt, model_validator

from sema.registry.base import SemaType
from sema.registry.enums.gw1_emission_method import Gw1EmissionMethod
from sema.registry.enums.gw1_unit import Gw1Unit
from sema.registry.property_format import LeftRightDot, SpaceheatName, UUID4Str


class DerivedChannelGt(SemaType):
    """Sema: https://schemas.electricity.works/types/derived.channel.gt/001"""

    id: UUID4Str
    name: SpaceheatName
    created_by_node_name: SpaceheatName
    strategy: SpaceheatName
    input_channel_names: list[SpaceheatName]
    output_unit: Gw1Unit | None = None
    emission_method: Gw1EmissionMethod
    async_emit_delta: PositiveInt | None = None
    emit_period_s: PositiveInt | None = None
    parameters: dict[str, Any] | None = None
    display_name: str
    terminal_asset_alias: LeftRightDot
    type_name: Literal["derived.channel.gt"] = "derived.channel.gt"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DerivedChannelGt":
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
