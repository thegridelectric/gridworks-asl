from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.g_node_reparent_cmd import GNodeReparentCmd


class GNodeReparentCmd000(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.reparent.cmd/000"""

    new_node: GNodeGt
    moved_child_g_node_ids: list[UUID4Str]
    type_name: Literal["g.node.reparent.cmd"] = "g.node.reparent.cmd"
    version: Literal["000"] = "000"

    def upgrade(self) -> GNodeReparentCmd:
        """
        - Proof: new optional opaque authorization artifact for this re-parent
        (format is machinery of the authority substrate, mirroring
        g.node.create.cmd)
        """
        data = self.model_dump(exclude_none=True)
        data["version"] = "001"
        return GNodeReparentCmd.model_validate(data)
