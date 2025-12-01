from typing import Literal

from gwasl.registry.base import AslType
from pydantic import model_validator
from typing_extensions import Self

from gwasl.registry.property_format import (
    HandleName,
    LeftRightDot,
    UTCMilliseconds,
)


class MachineStates(AslType):
    """ """

    MachineHandle: HandleName
    StateEnum: LeftRightDot
    StateList: list[str]
    UnixMsList: list[UTCMilliseconds]
    TypeName: Literal["machine.states"] = "machine.states"
    Version: str = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: list Length Consistency.
        StateList and UnixMsList must have the same length
        """
        # Implement check for axiom 1"
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: If StateEnum is a recognized GridWorks enum, then the StateList elements are all values of that enum..

        """
        # Implement check for axiom 2"
        return self
