from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.connectivity_edge_gt import ConnectivityEdgeGt
from sema.runtime.types.g_node_gt import GNodeGt


class GNodeForest(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.forest/001"""

    roots: list[LeftRightDot]
    nodes: list[GNodeGt]
    edges: list[ConnectivityEdgeGt]
    send_time_ms: UTCMilliseconds | None = None
    proof: str | None = None
    type_name: Literal["g.node.forest"] = "g.node.forest"
    version: Literal["001"] = "001"
