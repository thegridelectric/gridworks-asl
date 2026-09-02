from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1SimDeviceType(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.sim.device.type/000"""

    SimSensor = auto()
    SimRelayBank = auto()
    SimPowerMeter = auto()
    SimGw108 = auto()
    SimSamsungAE055FEYMCG = auto()
    SimHpOdu = auto()
    SimHpIdu = auto()

    @classmethod
    def default(cls) -> "Gw1SimDeviceType":
        return cls.SimSensor

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.sim.device.type"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
