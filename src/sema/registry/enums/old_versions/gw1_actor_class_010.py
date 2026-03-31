from enum import auto

from sema.registry.enums.gw_str_enum import SemaEnum


class Gw1ActorClass010(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.actor.class/010"""

    NoActor = auto()
    PrimaryScada = auto()
    SecondaryScada = auto()
    PowerMeter = auto()
    LocalControl = auto()
    LeafAlly = auto()
    DerivedGenerator = auto()
    PicoCycler = auto()
    HpBoss = auto()
    I2cRelayMultiplexer = auto()
    I2cZeroTenMultiplexer = auto()
    Hubitat = auto()
    Relay = auto()
    MultipurposeSensor = auto()
    HoneywellThermostat = auto()
    ApiTankModule = auto()
    ApiFlowModule = auto()
    ZeroTenOutputer = auto()
    ApiBtuMeter = auto()
    SiegLoop = auto()
    GpioSensor = auto()
    I2cBus = auto()
    I2cRelayBoard = auto()

    @classmethod
    def default(cls) -> "Gw1ActorClass010":
        return cls.NoActor

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.actor.class"

    @classmethod
    def enum_version(cls) -> str:
        return "010"
