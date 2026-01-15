from enum import auto

from gwasl.registry.enums.gw_str_enum import AslEnum


class RelayClosedOrOpen(AslEnum):
    RelayClosed = auto()
    RelayOpen = auto()

    @classmethod
    def values(cls) -> list[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]

    @classmethod
    def default(cls) -> "RelayClosedOrOpen":
        return cls.RelayClosed

    @classmethod
    def enum_name(cls) -> str:
        return "relay.closed.or.open"
