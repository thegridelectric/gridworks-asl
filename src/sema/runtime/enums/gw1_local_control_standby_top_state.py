from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1LocalControlStandbyTopState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.local.control.standby.top.state/001"""

    EverythingOff = auto()
    Dormant = auto()

    @classmethod
    def default(cls) -> "Gw1LocalControlStandbyTopState":
        return cls.EverythingOff

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.local.control.standby.top.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
