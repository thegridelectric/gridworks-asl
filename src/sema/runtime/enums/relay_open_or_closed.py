from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class RelayOpenOrClosed(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/relay.open.or.closed/000"""

    RelayClosed = auto()
    RelayOpen = auto()

    @classmethod
    def default(cls) -> "RelayOpenOrClosed":
        return cls.RelayClosed

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "relay.open.or.closed"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
