from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.enums.relay_closed_or_open import RelayClosedOrOpen
from sema.registry.property_format import HandleName, LeftRightDot, UTCMilliseconds


def _validate_known_state_enum(state_enum: str, states: list[str]) -> None:
    if state_enum == "relay.closed.or.open":
        valid_values = set(RelayClosedOrOpen.values())
        invalid = [state for state in states if state not in valid_values]
        if invalid:
            raise ValueError(
                "Axiom 2 failed: state_list contains invalid values for relay.closed.or.open."
            )


class MachineStates(SemaType):
    """Sema: https://schemas.electricity.works/types/machine.states/000"""

    machine_handle: HandleName
    state_enum: LeftRightDot
    state_list: list[str]
    unix_ms_list: list[UTCMilliseconds]
    type_name: Literal["machine.states"] = "machine.states"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "MachineStates":
        if len(self.state_list) != len(self.unix_ms_list):
            raise ValueError(
                "Axiom 1 failed: state_list and unix_ms_list must have equal length."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "MachineStates":
        _validate_known_state_enum(self.state_enum, self.state_list)
        return self
