from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1LcTopState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.lc.top.state/001"""

    Dormant = auto()
    UsingNonElectricBackup = auto()
    Normal = auto()
    ScadaBlind = auto()
    Monitor = auto()

    @classmethod
    def default(cls) -> "Gw1LcTopState":
        return cls.Dormant

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.lc.top.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
