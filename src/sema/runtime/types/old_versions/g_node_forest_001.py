from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.connectivity_edge_gt import ConnectivityEdgeGt
from sema.runtime.types.g_node_forest import GNodeForest
from sema.runtime.types.old_versions.g_node_gt_005 import GNodeGt005


class GNodeForest001(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.forest/001"""

    roots: list[LeftRightDot]
    nodes: list[GNodeGt005]
    edges: list[ConnectivityEdgeGt]
    send_time_ms: UTCMilliseconds | None = None
    proof: str | None = None
    type_name: Literal["g.node.forest"] = "g.node.forest"
    version: Literal["001"] = "001"

    def upgrade(self) -> GNodeForest:
        """
        - Nodes rebind to g.node.gt:006; SendTimeMs joins required
        """
        if self.send_time_ms is None:
            raise self.upgrade_requires_context(
                "g.node.forest:001 -> 002 requires SendTimeMs; an instance "
                "without one cannot be upgraded (a send time is never "
                "fabricated)"
            )
        data = self.model_dump(exclude_none=True)
        data["version"] = "002"
        for node in data["nodes"]:
            node["version"] = "006"
        return GNodeForest.model_validate(data)
