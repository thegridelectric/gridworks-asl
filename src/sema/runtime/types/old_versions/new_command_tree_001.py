from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.new_command_tree import NewCommandTree
from sema.runtime.types.old_versions.spaceheat_node_gt_301 import SpaceheatNodeGt301
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class NewCommandTree001(SemaType):
    """Sema: https://schemas.electricity.works/types/new.command.tree/001"""

    from_g_node_alias: LeftRightDot
    sh_nodes: list[SpaceheatNodeGt301]
    unix_ms: UTCMilliseconds
    type_name: Literal["new.command.tree"] = "new.command.tree"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "NewCommandTree001":
        """
        Axiom 1: PrefixClosedHandles
        Let the effective handle of an ShNode be its Handle if present, otherwise its Name.
        The set of effective handles SHALL be prefix-closed: for every ShNode in ShNodes,
        each dot-separated prefix of its effective handle SHALL also be the effective handle
        of some ShNode in ShNodes.
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

    def upgrade(self) -> NewCommandTree:
        """- ShNodes: spaceheat.node.gt:301 -> 303"""
        data = self.model_dump()
        lifted: list[SpaceheatNodeGt] = []
        for node in self.sh_nodes:
            current: SemaType = node
            while not isinstance(current, SpaceheatNodeGt):
                current = current.upgrade()
            lifted.append(current)
        data["sh_nodes"] = lifted
        data["version"] = "002"
        return NewCommandTree.model_validate(data)
