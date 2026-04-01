from typing import Literal
from typing_extensions import Self

from sema.runtime.base import SemaType
from pydantic import model_validator

from sema.runtime.enums import BaseGNodeClass, GNodeStatus
from sema.runtime.property_format import (
    LeftRightDot,
    UUID4Str,
)


class GNodeGt(SemaType):
    """
    Sema: https://schemas.electricity.works/types/g.node.gt/004
    """
    g_node_id: UUID4Str
    alias: LeftRightDot
    base_class: BaseGNodeClass
    g_node_class: str # organization-specific functional role
    status: GNodeStatus
    prev_alias: LeftRightDot | None = None
    position_point_id: UUID4Str | None = None
    display_name: str | None = None
    type_name: Literal["g.node.gt"] = "g.node.gt"
    version: Literal["004"] = "004"

    @model_validator(mode="after") 
    def check_axiom_1(self) -> Self: 
        """
        Axiom 1: Physical class aligment. For physical GNodes 
        (BaseClass != Logical), GNodeClass must match the BaseClass 
        name exactly.
        """
        if self.base_class != BaseGNodeClass.Logical:
            if self.g_node_class != self.base_class.value:
                raise ValueError(
                    f"Axiom 1 violated! Physical GNodes must align BaseClass and GNodeClass. "
                    f"Expected GNodeClass='{self.base_class.value}' "
                    f"but got '{self.g_node_class}'."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: Physical GNodes have locations.
        If BaseClass != Logical, PositionPointId must not be null.
        """
        if self.base_class != BaseGNodeClass.Logical:
            if self.position_point_id is None:
                raise ValueError(
                    "Axiom 2 violated! Physical GNodes must have a PositionPointId. "
                    f"BaseClass='{self.base_class.value}' has no location."
                )
        return self