from typing import Literal
from pydantic import ConfigDict, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_013 import Gw1ActorClass013
from sema.runtime.property_format import HandleName
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class SpaceheatNodeGt302(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/302"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: Gw1ActorClass013
    display_name: str | None = None
    component_id: UUID4Str | None = None
    board_component_id: UUID4Str | None = None
    nameplate_power_w: PositiveInt | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["302"] = "302"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatNodeGt302":
        """
        Axiom 1: ActorHierarchyConstraints
        If ActorClass is "NoActor", ActorHierarchyName SHALL be absent. If ActorClass is not
        "NoActor" and ActorHierarchyName is absent, then ActorClass SHALL be "PrimaryScada"
        or "SecondaryScada". If ActorHierarchyName is present, its final segment SHALL equal
        Name and all segments SHALL be unique.
        """
        if self.actor_class == Gw1ActorClass013.NoActor:
            if self.actor_hierarchy_name is not None:
                raise ValueError(
                    "Axiom 1 failed: actor_hierarchy_name must be absent when actor_class is NoActor."
                )
            return self

        if self.actor_hierarchy_name is None:
            if self.actor_class not in {
                Gw1ActorClass013.PrimaryScada,
                Gw1ActorClass013.SecondaryScada,
            }:
                raise ValueError(
                    "Axiom 1 failed: only PrimaryScada or SecondaryScada may omit actor_hierarchy_name."
                )
            return self

        segments = self.actor_hierarchy_name.split(".")
        if segments[-1] != self.name or len(set(segments)) != len(segments):
            raise ValueError(
                "Axiom 1 failed: actor_hierarchy_name must end with name and have unique segments."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "SpaceheatNodeGt302":
        """
        Axiom 2: HandleConstraints
        If Handle is present, its final segment SHALL equal Name and all segments SHALL be
        unique.
        """
        if self.handle is None:
            return self
        segments = self.handle.split(".")
        if segments[-1] != self.name or len(set(segments)) != len(segments):
            raise ValueError(
                "Axiom 2 failed: handle must end with name and have unique segments."
            )
        return self

    def upgrade(self) -> SpaceheatNodeGt:
        """
        - ActorClass: gw1.actor.class:013 -> 014 (adds FiveVBoss)
        """
        data = self.model_dump()
        data["version"] = "303"
        return SpaceheatNodeGt.model_validate(data)
