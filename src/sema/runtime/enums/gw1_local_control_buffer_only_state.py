from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1LocalControlBufferOnlyState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.local.control.buffer.only.state/001"""

    Initializing = auto()
    HpOn = auto()
    HpOff = auto()
    Dormant = auto()

    @classmethod
    def default(cls) -> "Gw1LocalControlBufferOnlyState":
        return cls.Initializing

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.local.control.buffer.only.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
