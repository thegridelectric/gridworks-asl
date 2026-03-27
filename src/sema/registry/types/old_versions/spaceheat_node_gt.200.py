from typing import Literal, Optional

from sema.registry.base import SemaType, snake_to_pascal
from pydantic import ConfigDict, StrictInt, model_validator
from typing_extensions import Self

from sema.registry.property_format import HandleName, SpaceheatName, UUID4Str


class SpaceheatNodeGt(SemaType):
    Name: SpaceheatName
    ActorHierarchyName: Optional[HandleName] = None
    Handle: Optional[HandleName] = None
    ActorClass: str
    DisplayName: Optional[str] = None
    ComponentId: Optional[str] = None
    NameplatePowerW: Optional[StrictInt] = None
    InPowerMetering: Optional[bool] = None
    ShNodeId: UUID4Str
    TypeName: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    Version: Literal["200"] = "200"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: InPowerMetering requirements.
        If InPowerMetering exists and is true, then NameplatePowerW must exist
        """
        if self.InPowerMetering and self.NameplatePowerW is None:
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
