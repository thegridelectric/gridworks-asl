from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GwHouse0PrimaryFlowSource
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.types.gw1_hvac_zone import Gw1HvacZone


class GwHouse0Hydronic(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.house0.hydronic/000"""

    zones: list[Gw1HvacZone]
    total_store_tanks: NonNegativeInt
    use_sieg_loop: bool
    sieg_loop_plumbed: bool
    primary_flow_source: GwHouse0PrimaryFlowSource
    strategy: str
    type_name: Literal["gw.house0.hydronic"] = "gw.house0.hydronic"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: SiegLoopControlImpliesPlumbed
        If UseSiegLoop is true then SiegLoopPlumbed SHALL be true — the scada
        cannot run the Siegenthaler loop unless it is plumbed.
        """
        if self.use_sieg_loop and not self.sieg_loop_plumbed:
            raise ValueError(
                "Axiom 1 (SiegLoopControlImpliesPlumbed) failed: UseSiegLoop requires "
                "SiegLoopPlumbed to be true."
            )
        return self
