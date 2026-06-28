from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GNodeStatus
from sema.runtime.property_format import UUID4Str


class ConnectivityEdgeGt(SemaType):
    """Sema: https://schemas.electricity.works/types/connectivity.edge.gt/000"""

    id: UUID4Str
    from_g_node_id: UUID4Str
    to_g_node_id: UUID4Str
    status: GNodeStatus
    type_name: Literal["connectivity.edge.gt"] = "connectivity.edge.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ConnectivityEdgeGt":
        """
        Axiom 1: NoSelfLoop
        FromGNodeId SHALL NOT equal ToGNodeId.
        """
        if self.from_g_node_id == self.to_g_node_id:
            raise ValueError(
                "Axiom 1 failed: from_g_node_id and to_g_node_id must differ."
            )
        return self
