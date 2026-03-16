from enum import auto
from typing import List

from sema.registry.enums.gw_str_enum import SemaEnum


class ActorClass(SemaEnum):
    """ Sema: https://schemas.electricity.works/enums/sh.actor.class/007"""

    NoActor = auto()
    Scada = auto()
    HomeAlone = auto()
    BooleanActuator = auto()
    PowerMeter = auto()
    Atn = auto()
    SimpleSensor = auto()
    MultipurposeSensor = auto()
    Thermostat = auto()
    HubitatTelemetryReader = auto()
    HubitatTankModule = auto()
    HubitatPoller = auto()
    I2cRelayMultiplexer = auto()
    FlowTotalizer = auto()
    Relay = auto()
    Admin = auto()
    Fsm = auto()
    Parentless = auto()
    Hubitat = auto()
    HoneywellThermostat = auto()
    ApiTankModule = auto()
    ApiFlowModule = auto()
    PicoCycler = auto()
    I2cDfrMultiplexer = auto()
    ZeroTenOutputer = auto()
    AtomicAlly = auto()
    SynthGenerator = auto()
    FakeAtn = auto()
    PumpDoctor = auto()
    StratBoss = auto()
    HpRelayBoss = auto()
    SiegLoop = auto()
    HpBoss = auto()

    @classmethod
    def default(cls) -> "ActorClass":
        return cls.NoActor

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "sh.actor.class"

    @classmethod
    def enum_version(cls) -> str:
        return "007"
