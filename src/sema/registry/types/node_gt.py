from typing import Literal

from sema.registry.base import SemaType, snake_to_pascal
from pydantic import ConfigDict, StrictInt, model_validator
from typing_extensions import Self

from sema.registry.property_format import HandleName, SpaceheatName, UUID4Str


class NodeGt(SemaType):
    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: str | None = None
    display_name: str | None = None
    component_id: str | None = None
    nameplate_power_w: StrictInt | None = None
    in_power_mtering: bool | None = None
    node_id: UUID4Str
    type_name: Literal["node.gt"] = "node.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: InPowerMetering requirements.
        If InPowerMetering exists and is true, then NameplatePowerW must exist
        """
        if self.in_power_mtering and self.nameplate_power_w is None:
            raise ValueError(
                "Axiom 1 failed! "
                "If InPowerMetering exists and is true, then NameplatePowerW must exist"
            )
        return self

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

