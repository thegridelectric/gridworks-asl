from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.g_node_gt import GNodeGt


class GNodeTopologyBroadcast(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.topology.broadcast/000"""

    updated_nodes: list[GNodeGt]
    type_name: Literal["g.node.topology.broadcast"] = "g.node.topology.broadcast"
    version: Literal["000"] = "000"
