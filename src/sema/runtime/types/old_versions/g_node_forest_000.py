from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.types.connectivity_edge_gt import ConnectivityEdgeGt
from sema.runtime.types.old_versions.g_node_forest_001 import GNodeForest001
from sema.runtime.types.old_versions.g_node_gt_005 import GNodeGt005


class GNodeForest000(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.forest/000"""

    roots: list[LeftRightDot]
    nodes: list[GNodeGt005]
    edges: list[ConnectivityEdgeGt]
    proof: str | None = None
    type_name: Literal["g.node.forest"] = "g.node.forest"
    version: Literal["000"] = "000"

    def upgrade(self) -> GNodeForest001:
        """
        - SendTimeMs: new optional sender-clock stamp (epoch ms) at forest
        assembly; the registry stamps wall-clock — it is never simulated
        (sender-time standard, first adopter)
        """
        data = self.model_dump(exclude_none=True)
        data["version"] = "001"
        return GNodeForest001.model_validate(data)
