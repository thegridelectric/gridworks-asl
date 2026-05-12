from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1LeafAllyBufferOnlyState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.leaf.ally.buffer.only.state/001"""

    Dormant = auto()
    Initializing = auto()
    HpOn = auto()
    HpOff = auto()
    HpOffNonElectricBackup = auto()

    @classmethod
    def default(cls) -> "Gw1LeafAllyBufferOnlyState":
        return cls.Dormant

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.leaf.ally.buffer.only.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
