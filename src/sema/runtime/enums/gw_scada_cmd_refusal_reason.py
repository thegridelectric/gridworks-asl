from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class GwScadaCmdRefusalReason(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw.scada.cmd.refusal.reason/000"""

    Unknown = auto()
    Busy = auto()
    NotMyBoss = auto()
    UnknownEvent = auto()
    OutOfRange = auto()
    NotAControlNode = auto()

    @classmethod
    def default(cls) -> "GwScadaCmdRefusalReason":
        return cls.Unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw.scada.cmd.refusal.reason"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
