from typing import Literal
from pydantic import model_validator
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

    @model_validator(mode="after")
    def check_axiom_1(self) -> "NewCommandTree":
        """
        Axiom 1: PrefixClosedHierarchy
        a. The set of ShNode Handles SHALL be prefix-closed: for every ShNode in ShNodes
        whose Handle is present, each of its dot-separated prefixes SHALL also be the Handle
        of some ShNode in ShNodes.
        b. The set of ShNode ActorHierarchyNames SHALL be prefix-closed in the same way: for
        every ShNode in ShNodes whose ActorHierarchyName is present, each of its
        dot-separated prefixes SHALL also be the ActorHierarchyName of some ShNode in
        ShNodes.
        """
        for attr in ("handle", "actor_hierarchy_name"):
            present = {
                getattr(node, attr)
                for node in self.sh_nodes
                if getattr(node, attr) is not None
            }
            for value in present:
                segments = value.split(".")
                for n in range(1, len(segments)):
                    prefix = ".".join(segments[:n])
                    if prefix not in present:
                        raise ValueError(
                            f"Axiom 1 failed: {attr} {value!r} has prefix {prefix!r} "
                            f"that is not the {attr} of any ShNode."
                        )
        return self
