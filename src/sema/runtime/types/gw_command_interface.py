from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import ChangeRelayState
from sema.runtime.enums import HpBossState
from sema.runtime.enums import PicoCyclerState
from sema.runtime.enums import RebootPicos
from sema.runtime.enums import RelayClosedOrOpen
from sema.runtime.enums import TurnHpOnOff
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.gw_command_transition import GwCommandTransition


class GwCommandInterface(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.command.interface/000"""

    actor_name: SpaceheatName
    event_type: LeftRightDot
    state_type: LeftRightDot
    commands: list[GwCommandTransition]
    type_name: Literal["gw.command.interface"] = "gw.command.interface"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwCommandInterface":
        """
        Axiom 1: NonEmptyCommands
        Commands SHALL be non-empty.
        """
        if not self.commands:
            raise ValueError("Axiom 1 failed: commands must be non-empty.")
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwCommandInterface":
        """
        Axiom 2: EventsAreVocabulary
        If EventType equals "change.relay.state", "turn.hp.on.off" or "reboot.picos", every
        Commands entry's Event SHALL be a value of change.relay.state:000,
        turn.hp.on.off:000 or reboot.picos:000 respectively.
        """
        vocabulary = {
            "change.relay.state": set(ChangeRelayState.values()),
            "turn.hp.on.off": set(TurnHpOnOff.values()),
            "reboot.picos": set(RebootPicos.values()),
        }
        valid = vocabulary.get(self.event_type)
        if valid is not None:
            for command in self.commands:
                if command.event not in valid:
                    raise ValueError(
                        f"Axiom 2 failed: event {command.event!r} is not a value of "
                        f"{self.event_type}."
                    )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwCommandInterface":
        """
        Axiom 3: StatesAreVocabulary
        If StateType equals "relay.closed.or.open", "hp.boss.state" or "pico.cycler.state",
        every Commands entry's ToState SHALL be a value of relay.closed.or.open:000,
        hp.boss.state:000 or pico.cycler.state:000 respectively.
        """
        vocabulary = {
            "relay.closed.or.open": set(RelayClosedOrOpen.values()),
            "hp.boss.state": set(HpBossState.values()),
            "pico.cycler.state": set(PicoCyclerState.values()),
        }
        valid = vocabulary.get(self.state_type)
        if valid is not None:
            for command in self.commands:
                if command.to_state not in valid:
                    raise ValueError(
                        f"Axiom 3 failed: state {command.to_state!r} is not a value of "
                        f"{self.state_type}."
                    )
        return self
