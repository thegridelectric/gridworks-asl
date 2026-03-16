from typing import Optional

from sema.registry.base import SemaType
from pydantic import ConfigDict, PositiveInt, model_validator
from typing_extensions import Self

from sema.registry.enums import MakeModel
from sema.registry.property_format import UUID4Str
from sema.registry.type_helpers.device_by_make_model import DEVICE_BY_MAKE_MODEL


class GwDeviceType(SemaType):
    Id: UUID4Str
    DisplayName: Optional[str] = None
    Name: MakeModel
    TypeName: str = "gw.device.type"
    Version: str = "000"

    model_config = ConfigDict(use_enum_values=True, extra="allow")

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: DeviceType captured by MakeModel
                If d is a DeviceType,
        then
           - EITHER  its (Name, Id) must be a key,value pair in
        DEVICE_BY_MAKE_MODEL (below)
           - XOR its Name is MakeModel.UNKNOWNMAKE__UNKNOWNMODEL

        """
        if (
            self.Name not in DEVICE_BY_MAKE_MODEL
            and self.Name is not MakeModel.default().value
        ):
            raise ValueError(
                "Axiom 1 violated! If MakeModel not in this list, "
                f"must be UNKNOWN: {DEVICE_BY_MAKE_MODEL}"
            )
        if self.Name is MakeModel.default().value:
            if self.Id in DEVICE_BY_MAKE_MODEL.values():
                raise ValueError(
                    f"Id {self.Id} already used by known MakeModel!"
                )
        elif self.Id != DEVICE_BY_MAKE_MODEL[self.Name]:
            raise ValueError(
                f"Axiom 1 violated! DeviceType {self.Name} must have "
                f"id {DEVICE_BY_MAKE_MODEL[self.Name]}!"
            )
        return self
