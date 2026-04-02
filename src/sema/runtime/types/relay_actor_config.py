from typing import Literal

from pydantic import StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.change_relay_state import ChangeRelayState
from sema.runtime.enums.relay_closed_or_open import RelayClosedOrOpen
from sema.runtime.enums.relay_wiring_config import RelayWiringConfig
from sema.runtime.enums.spaceheat_unit import SpaceheatUnit
from sema.runtime.property_format import LeftRightDot, PositiveInt, SpaceheatName


class RelayActorConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/relay.actor.config/003"""

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
    version: Literal["003"] = "003"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "RelayActorConfig":
        """
        Axiom 1: AsyncCaptureConsistency
        If AsyncCapture is true, then AsyncCaptureDelta SHALL be present.
        """
        if self.async_capture and self.async_capture_delta is None:
            raise ValueError(
                "Axiom 1 failed: async_capture requires async_capture_delta."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "RelayActorConfig":
        """
        Axiom 2: CapturePollingConsistency
        If PollPeriodMs is present, then CapturePeriodMs (CapturePeriodS * 1000)
        SHALL be greater than PollPeriodMs. If CapturePeriodMs is less than
        10 times PollPeriodMs, then CapturePeriodMs SHALL be a multiple of
        PollPeriodMs.
        """
        if self.poll_period_ms is None:
            return self

        capture_period_ms = self.capture_period_s * 1000
        if capture_period_ms <= self.poll_period_ms:
            raise ValueError(
                "Axiom 2 failed: capture_period_s * 1000 must be greater than poll_period_ms."
            )
        if (
            capture_period_ms < 10 * self.poll_period_ms
            and capture_period_ms % self.poll_period_ms != 0
        ):
            raise ValueError(
                "Axiom 2 failed: capture period must be a multiple of poll period when "
                "capture_period_ms is less than 10 times poll_period_ms."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "RelayActorConfig":
        """
        Axiom 3: RelayEventEnumConsistency
        If EventType equals "change.relay.state", then DeEnergizingEvent and
        EnergizingEvent SHALL both be valid values of change.relay.state:000.
        """
        if self.event_type == "change.relay.state":
            valid = set(ChangeRelayState.values())
            if self.de_energizing_event not in valid or self.energizing_event not in valid:
                raise ValueError(
                    "Axiom 3 failed: relay state events must be valid change.relay.state values."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "RelayActorConfig":
        """
        Axiom 4: RelayStateEnumConsistency
        If StateType equals "relay.closed.or.open", then DeEnergizedState and
        EnergizedState SHALL both be valid values of relay.closed.or.open:000.
        """
        if self.state_type == "relay.closed.or.open":
            valid = set(RelayClosedOrOpen.values())
            if self.de_energized_state not in valid or self.energized_state not in valid:
                raise ValueError(
                    "Axiom 4 failed: relay states must be valid relay.closed.or.open values."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_5(self) -> "RelayActorConfig":
        """
        Axiom 5: RelayEventStateMatch
        If EventType equals "change.relay.state" and StateType equals
        "relay.closed.or.open", then each relay event SHALL imply its matching
        relay state.
        """
        if self.state_type != "relay.closed.or.open" or self.event_type != "change.relay.state":
            return self

        event_to_state = {
            "CloseRelay": "RelayClosed",
            "OpenRelay": "RelayOpen",
        }
        if event_to_state.get(self.de_energizing_event) != self.de_energized_state:
            raise ValueError(
                "Axiom 5 failed: de_energizing_event is inconsistent with de_energized_state."
            )
        if event_to_state.get(self.energizing_event) != self.energized_state:
            raise ValueError(
                "Axiom 5 failed: energizing_event is inconsistent with energized_state."
            )
        return self
