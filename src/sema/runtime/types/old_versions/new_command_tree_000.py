from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.old_versions.new_command_tree_001 import NewCommandTree001
from sema.runtime.types.old_versions.spaceheat_node_gt_200 import SpaceheatNodeGt200
from sema.runtime.types.old_versions.spaceheat_node_gt_300 import SpaceheatNodeGt300
from sema.runtime.types.old_versions.spaceheat_node_gt_301 import SpaceheatNodeGt301


class NewCommandTree000(SemaType):
    """Sema: https://schemas.electricity.works/types/new.command.tree/000"""

    from_g_node_alias: LeftRightDot
    sh_nodes: list[SpaceheatNodeGt200 | SpaceheatNodeGt300 | SpaceheatNodeGt301]
    unix_ms: UTCMilliseconds
    type_name: Literal["new.command.tree"] = "new.command.tree"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "NewCommandTree000":
        """
        Axiom 1: PrefixClosedHandles
        Let the effective handle of an ShNode be its Handle if present, otherwise
        its Name. The set of effective handles SHALL be prefix-closed: for every ShNode
        in ShNodes, each dot-separated prefix of its effective handle SHALL also be the
        effective handle of some ShNode in ShNodes.
        """
        effective = {
            node.handle if node.handle is not None else node.name
            for node in self.sh_nodes
        }
        for value in effective:
            segments = value.split(".")
            for n in range(1, len(segments)):
                prefix = ".".join(segments[:n])
                if prefix not in effective:
                    raise ValueError(
                        f"Axiom 1 failed: effective handle {value!r} has "
                        f"prefix {prefix!r} that is not the effective handle "
                        "of any ShNode."
                    )
        return self

    def upgrade(self) -> NewCommandTree001:
        """- ShNodes: spaceheat.node.gt:301 only (drop the multi-version oneOf; retroactive registration of the wire version the spruce scada emitted from 2026-01-28)"""
        data = self.model_dump()
        lifted: list[SpaceheatNodeGt301] = []
        for node in self.sh_nodes:
            current: SemaType = node
            while not isinstance(current, SpaceheatNodeGt301):
                current = current.upgrade()
            lifted.append(current)
        data["sh_nodes"] = lifted
        data["version"] = "001"
        return NewCommandTree001.model_validate(data)
