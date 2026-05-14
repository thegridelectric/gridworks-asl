from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.old_versions.spaceheat_node_gt_200 import SpaceheatNodeGt200


class NewCommandTree(SemaType):
    """Sema: https://schemas.electricity.works/types/new.command.tree/000"""

    from_g_node_alias: LeftRightDot
    sh_nodes: list[SpaceheatNodeGt200]
    unix_ms: UTCMilliseconds
    type_name: Literal["new.command.tree"] = "new.command.tree"
    version: Literal["000"] = "000"
