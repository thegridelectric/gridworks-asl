from typing import Literal

from pydantic import StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.change_relay_state import ChangeRelayState
from sema.runtime.enums.relay_closed_or_open import RelayClosedOrOpen
from sema.runtime.enums.relay_wiring_config import RelayWiringConfig
from sema.runtime.enums.spaceheat_unit import SpaceheatUnit
from sema.runtime.property_format import LeftRightDot, PositiveInt, SpaceheatName
from sema.runtime.types.relay_actor_config import RelayActorConfig as RelayActorConfig003

class RelayActorConfig002(SemaType):
    """Sema: https://schemas.electricity.works/types/relay.actor.config/002"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    relay_idx: PositiveInt
    actor_name: SpaceheatName
    wiring_config: RelayWiringConfig
    event_type: LeftRightDot
    de_energizing_event: str
    energizing_event: str
    state_type: LeftRightDot
    de_energized_state: str
    energized_state: str
    type_name: Literal["relay.actor.config"] = "relay.actor.config"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "RelayActorConfig002":
        if self.event_type == "change.relay.state":
            valid = set(ChangeRelayState.values())
            if self.de_energizing_event not in valid or self.energizing_event not in valid:
                raise ValueError(
                    "Axiom 1 failed: relay state events must be valid change.relay.state values."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "RelayActorConfig002":
        if self.state_type == "relay.closed.or.open":
            valid = set(RelayClosedOrOpen.values())
            if self.de_energized_state not in valid or self.energized_state not in valid:
                raise ValueError(
                    "Axiom 2 failed: relay states must be valid relay.closed.or.open values."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "RelayActorConfig002":
        if self.state_type != "relay.closed.or.open" or self.event_type != "change.relay.state":
            return self

        if self.wiring_config == RelayWiringConfig.NormallyClosed:
            expected = (
                ("RelayClosed", "CloseRelay"),
                ("RelayOpen", "OpenRelay"),
            )
        elif self.wiring_config == RelayWiringConfig.NormallyOpen:
            expected = (
                ("RelayOpen", "OpenRelay"),
                ("RelayClosed", "CloseRelay"),
            )
        else:
            return self

        de_state, de_event = expected[0]
        en_state, en_event = expected[1]
        if (
            self.de_energized_state != de_state
            or self.de_energizing_event != de_event
            or self.energized_state != en_state
            or self.energizing_event != en_event
        ):
            raise ValueError(
                "Axiom 4 failed: wiring_config is inconsistent with relay event/state semantics."
            )
        return self

    def upgrade(self) -> RelayActorConfig003:
        """002 -> 003 Require AsyncCaptureDelta when AsyncCapture is true"""
        data = self.model_dump()

        if self.async_capture:
            if not self.async_capture_delta:
                data["async_capture_delta"] = 1

        # Update version
        data["version"] = "003"

        return RelayActorConfig003.model_validate(data)