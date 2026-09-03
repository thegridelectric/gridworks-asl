from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GwHouse0PrimaryFlowSource
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.gw1_hvac_zone import Gw1HvacZone
from sema.runtime.types.gw1_zone_call_circuit import Gw1ZoneCallCircuit


class GwHydronic(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.hydronic/000"""

    zones: list[Gw1HvacZone]
    zone_call_circuits: list[Gw1ZoneCallCircuit] | None = None
    total_store_tanks: NonNegativeInt
    primary_flow_source: GwHouse0PrimaryFlowSource
    hp_command_node_name: SpaceheatName | None = None
    type_name: Literal["gw.hydronic"] = "gw.hydronic"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: Cardinality
        a. TotalStoreTanks SHALL be between 1 and 6 inclusive.
        b. The number of Zones SHALL be between 1 and 6 inclusive.
        """
        if not 1 <= self.total_store_tanks <= 6:
            raise ValueError(
                "Axiom 1 (Cardinality) failed: TotalStoreTanks "
                f"({self.total_store_tanks}) must be between 1 and 6 inclusive."
            )
        if not 1 <= len(self.zones) <= 6:
            raise ValueError(
                "Axiom 1 (Cardinality) failed: number of Zones "
                f"({len(self.zones)}) must be between 1 and 6 inclusive."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: CircuitResolution
        a. Every circuit's ServesZone SHALL equal the Name of a zone in
        Zones. b. No two circuits SHALL share a CircuitPosition.
        """
        circuits = self.zone_call_circuits or []
        zone_names = {z.name for z in self.zones}
        for c in circuits:
            if c.serves_zone not in zone_names:
                raise ValueError(
                    "Axiom 2 (CircuitResolution) failed: ServesZone "
                    f"{c.serves_zone!r} does not name a zone in Zones."
                )
        positions = [c.circuit_position for c in circuits]
        if len(positions) != len(set(positions)):
            raise ValueError(
                "Axiom 2 (CircuitResolution) failed: CircuitPosition values "
                f"{positions} are not distinct."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> Self:
        """
        Axiom 3: LearnedNeedsTempChannel
        For every circuit whose SetpointSource is Learned, the zone named
        by its ServesZone SHALL carry a TempChannelName.
        """
        # String comparison, not an enum import: ZoneSetpointSource is not a
        # field enum of this type, and an absolute sema.runtime import would
        # break inside a restricted snapshot package.
        zones_by_name = {z.name: z for z in self.zones}
        for c in self.zone_call_circuits or []:
            zone = zones_by_name.get(c.serves_zone)
            if (
                c.setpoint_source == "Learned"
                and zone is not None
                and zone.temp_channel_name is None
            ):
                raise ValueError(
                    "Axiom 3 (LearnedNeedsTempChannel) failed: circuit at "
                    f"position {c.circuit_position} is Learned but zone "
                    f"{c.serves_zone!r} has no TempChannelName."
                )
        return self
