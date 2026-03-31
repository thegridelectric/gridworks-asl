from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.enums.relay_closed_or_open import RelayClosedOrOpen
from sema.registry.property_format import HandleName, LeftRightDot, UTCMilliseconds


class SingleMachineState(SemaType):
    """Sema: https://schemas.electricity.works/types/single.machine.state/000"""

    machine_handle: HandleName
    state_enum: LeftRightDot
    state: str
    unix_ms: UTCMilliseconds
    cause: str | None = None
    type_name: Literal["single.machine.state"] = "single.machine.state"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SingleMachineState":
        if (
            self.state_enum == "relay.closed.or.open"
            and self.state not in RelayClosedOrOpen.values()
        ):
            raise ValueError(
                "Axiom 1 failed: state must be a valid relay.closed.or.open value."
            )
        return self
