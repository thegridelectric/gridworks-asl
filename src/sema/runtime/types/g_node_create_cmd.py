from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.g_node_gt import GNodeGt


class GNodeCreateCmd(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.create.cmd/000"""

    new_node: GNodeGt
    proof: str | None = None
    type_name: Literal["g.node.create.cmd"] = "g.node.create.cmd"
    version: Literal["000"] = "000"
