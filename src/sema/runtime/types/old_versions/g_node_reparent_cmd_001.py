from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.g_node_reparent_cmd import GNodeReparentCmd
from sema.runtime.types.old_versions.g_node_gt_005 import GNodeGt005


class GNodeReparentCmd001(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.reparent.cmd/001"""

    new_node: GNodeGt005
    moved_child_g_node_ids: list[UUID4Str]
    proof: str | None = None
    type_name: Literal["g.node.reparent.cmd"] = "g.node.reparent.cmd"
    version: Literal["001"] = "001"

    def upgrade(self) -> GNodeReparentCmd:
        """
        - NewNode rebinds to g.node.gt:006
        """
        data = self.model_dump(exclude_none=True)
        data["version"] = "002"
        data["new_node"]["version"] = "006"
        return GNodeReparentCmd.model_validate(data)
