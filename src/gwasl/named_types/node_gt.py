"""Type node.gt, version 000"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, StrictInt, model_validator
from typing_extensions import Self

from gwasl.property_format import HandleName, SpaceheatName, UUID4Str


class NodeGt(BaseModel):
    Name: SpaceheatName
    ActorHierarchyName: Optional[HandleName] = None
    Handle: Optional[HandleName] = None
    ActorClass: Optional[str] = None
    DisplayName: Optional[str] = None
    ComponentId: Optional[str] = None
    NameplatePowerW: Optional[StrictInt] = None
    InPowerMetering: Optional[bool] = None
    ShNodeId: UUID4Str
    TypeName: Literal["node.gt"] = "node.gt"
    Version: Literal["000"] = "000"

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

    model_config = ConfigDict(extra="allow", use_enum_values=True)
