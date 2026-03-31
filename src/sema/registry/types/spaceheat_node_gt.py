from typing import Literal

from pydantic import ConfigDict, model_validator

from sema.registry.base import SemaType
from sema.registry.enums.gw1_actor_class import Gw1ActorClass
from sema.registry.property_format import HandleName, SpaceheatName, UUID4Str


class SpaceheatNodeGt(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/301"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: Gw1ActorClass
    display_name: str | None = None
    component_id: UUID4Str | None = None
    board_component_id: UUID4Str | None = None
    nameplate_power_w: int | None = None
    in_power_metering: bool | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["301"] = "301"

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatNodeGt":
        if self.in_power_metering and self.nameplate_power_w is None:
            raise ValueError(
                "Axiom 1 failed: nameplate_power_w is required when in_power_metering is true."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "SpaceheatNodeGt":
        if self.actor_class == Gw1ActorClass.NoActor:
            if self.actor_hierarchy_name is not None:
                raise ValueError(
                    "Axiom 2 failed: actor_hierarchy_name must be absent when actor_class is NoActor."
                )
            return self

        if self.actor_hierarchy_name is None:
            if self.actor_class not in {
                Gw1ActorClass.PrimaryScada,
                Gw1ActorClass.SecondaryScada,
            }:
                raise ValueError(
                    "Axiom 2 failed: only PrimaryScada or SecondaryScada may omit actor_hierarchy_name."
                )
            return self

        segments = self.actor_hierarchy_name.split(".")
        if segments[-1] != self.name or len(set(segments)) != len(segments):
            raise ValueError(
                "Axiom 2 failed: actor_hierarchy_name must end with name and have unique segments."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "SpaceheatNodeGt":
        if self.handle is None:
            return self
        segments = self.handle.split(".")
        if segments[-1] != self.name or len(set(segments)) != len(segments):
            raise ValueError(
                "Axiom 3 failed: handle must end with name and have unique segments."
            )
        return self
