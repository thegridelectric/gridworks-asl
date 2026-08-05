from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UtcIso8601Millis


class OperatingStateSequence(SemaType):
    """Sema: https://schemas.electricity.works/types/operating.state.sequence/000"""

    channel_name: SpaceheatName
    value_list: list[PascalCase]
    timestamp_list: list[UtcIso8601Millis]
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

    @model_validator(mode="after")
    def check_axiom_2(self) -> "OperatingStateSequence":
        """
        Axiom 2: StrictlyIncreasingTimestamps
        TimestampList SHALL be strictly increasing.
        """
        # utc.iso8601.millis is fixed-width UTC, so lexicographic order is
        # chronological order.
        for prev, nxt in zip(self.timestamp_list, self.timestamp_list[1:]):
            if not prev < nxt:
                raise ValueError(
                    "Axiom 2 failed: timestamp_list must be strictly increasing."
                )
        return self
