from typing import Literal, Dict, List, Set
from typing_extensions import Self

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.property_format import (
    UUID4Str,
    LeftRightDot,
    UTCMilliseconds,
)
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.g_node_instance_gt import GNodeInstanceGt
from sema.runtime.enums import GNodeInstanceStatus


class FisAuthorityManifest(SemaType):
    """
    Sema:
    https://schemas.electricity.works/types/fis.authority.manifest/000
    """

    snapshot_id: UUID4Str
    snapshot_taken_at_unix_ms: UTCMilliseconds

    parent_root_alias_list: List[LeftRightDot]
    g_node_list: List[GNodeGt]
    g_node_instance_list: List[GNodeInstanceGt]

    type_name: Literal["fis.authority.manifest"] = "fis.authority.manifest"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1:
        For every element in GNodeInstanceList, there SHALL exist
        exactly one element in GNodeList whose GNodeId matches
        the instance's GNodeId.
        """

        gnode_id_set: Set[str] = {g.g_node_id for g in self.g_node_list}

        for inst in self.g_node_instance_list:
            if inst.g_node_id not in gnode_id_set:
                raise ValueError(
                    f"Axiom 1 violated! Instance {inst.g_node_instance_id} "
                    f"references unknown GNodeId {inst.g_node_id}."
                )

        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: SingleActiveInstancePerGNode
        For each element in GNodeList, exactly one element in
        GNodeInstanceList SHALL have matching GNodeId and
        Status equal to Active.
        """

        # Map GNodeId -> active count
        active_counts: Dict[str, int] = {}

        for inst in self.g_node_instance_list:
            if inst.status == GNodeInstanceStatus.Active:
                active_counts[inst.g_node_id] = (
                    active_counts.get(inst.g_node_id, 0) + 1
                )

        for gnode in self.g_node_list:
            count = active_counts.get(gnode.g_node_id, 0)
            if count != 1:
                raise ValueError(
                    f"Axiom 2 violated! GNodeId {gnode.g_node_id} "
                    f"has {count} active instances (expected exactly 1)."
                )

        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> Self:
        """
        Axiom 3: ParentClosureUpToDeclaredRoots
        For every element in GNodeList, all alias prefixes of
        GNodeAlias SHALL also appear in GNodeList unless the prefix
        equals one of the aliases listed in ParentRootAliasList.
        """

        alias_set: Set[str] = {g.alias for g in self.g_node_list}
        root_set: Set[str] = set(self.parent_root_alias_list)

        for gnode in self.g_node_list:
            alias_parts = gnode.alias.split(".")

            # Walk prefixes from shortest to full
            for i in range(1, len(alias_parts)):
                prefix = ".".join(alias_parts[:i])

                if prefix in root_set:
                    break  # closure satisfied at declared root

                if prefix not in alias_set:
                    raise ValueError(
                        f"Axiom 3 violated! Alias '{gnode.alias}' "
                        f"is missing parent prefix '{prefix}' "
                        f"and it is not declared as a root."
                    )

        return self
