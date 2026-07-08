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

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: Cardinality
        a. TotalStoreTanks SHALL be between 1 and 6 inclusive.
        b. The number of Zones SHALL be between 1 and 6 inclusive.
        """
        if not 1 <= self.total_store_tanks <= 6:
            raise ValueError(
                "Axiom 2 (Cardinality) failed: TotalStoreTanks "
                f"({self.total_store_tanks}) must be between 1 and 6 inclusive."
            )
        if not 1 <= len(self.zones) <= 6:
            raise ValueError(
                "Axiom 2 (Cardinality) failed: number of Zones "
                f"({len(self.zones)}) must be between 1 and 6 inclusive."
            )
        return self
