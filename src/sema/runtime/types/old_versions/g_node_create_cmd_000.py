from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.g_node_create_cmd import GNodeCreateCmd
from sema.runtime.types.old_versions.g_node_gt_005 import GNodeGt005


class GNodeCreateCmd000(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.create.cmd/000"""

    new_node: GNodeGt005
    proof: str | None = None
    type_name: Literal["g.node.create.cmd"] = "g.node.create.cmd"
    version: Literal["000"] = "000"

    def upgrade(self) -> GNodeCreateCmd:
        """
        - NewNode rebinds to g.node.gt:006; new axiom 1 LocationlessAtCreation
        (NewNode.PositionPointId SHALL be null — a location identity is
        registered after creation)
        """
        if self.new_node.position_point_id is not None:
            raise self.upgrade_requires_context(
                "g.node.create.cmd:000 -> 001 forbids NewNode.PositionPointId; "
                "an instance carrying one cannot be upgraded without dropping "
                "data"
            )
        data = self.model_dump(exclude_none=True)
        data["version"] = "001"
        data["new_node"]["version"] = "006"
        return GNodeCreateCmd.model_validate(data)
