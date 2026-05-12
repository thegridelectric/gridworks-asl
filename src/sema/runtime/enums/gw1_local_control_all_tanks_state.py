from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1LocalControlAllTanksState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.local.control.all.tanks.state/001"""

    Initializing = auto()
    HpOnStoreOff = auto()
    HpOnStoreCharge = auto()
    HpOffStoreOff = auto()
    HpOffStoreDischarge = auto()
    Dormant = auto()

    @classmethod
    def default(cls) -> "Gw1LocalControlAllTanksState":
        return cls.Initializing

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.local.control.all.tanks.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
