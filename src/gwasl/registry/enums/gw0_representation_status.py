# Literal Enum:
#  - no additional values can be added over time.
#  - Sent as-is, not in hex symbol
from enum import auto
from typing import List

from gwasl.registry.enums.gw_str_enum import SemaEnum


class Gw0RepresentationStatus(SemaEnum):

    Unknown = auto()
    ListeningToAtn = auto()
    NotListeningToAtn = auto()

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]

    @classmethod
    def default(cls) -> "Gw0RepresentationStatus":
        return cls.Unknown

    @classmethod
    def enum_name(cls) -> str:
        return "gw0.representation.status"

    @classmethod
    def version(cls) -> str:
        return "000"
