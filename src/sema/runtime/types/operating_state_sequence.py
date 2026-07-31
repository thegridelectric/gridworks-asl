from typing import Any, Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UtcIso8601Seconds


class OperatingStateSequence(SemaType):
    """Sema: https://schemas.electricity.works/types/operating.state.sequence/000"""

    channel_name: SpaceheatName
    value_list: list[Any | None]
    timestamp_list: list[UtcIso8601Seconds]
    type_name: Literal["operating.state.sequence"] = "operating.state.sequence"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "OperatingStateSequence":
        """
        Axiom 1: ListLengthConsistency
        len(ValueList) SHALL equal len(TimestampList).
        """
        if len(self.value_list) != len(self.timestamp_list):
            raise ValueError(
                "Axiom 1 failed: value_list and timestamp_list must have equal length."
            )
        return self
