from enum import auto
from typing import List

from sema.registry.enums.gw_str_enum import SemaEnum


class MessageCategory(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/message.category/000
    """

    Unknown = auto()
    JsonDirect = auto()
    JsonBroadcast = auto()
    ScadaWrapped = auto()
    Serial = auto()

    @classmethod
    def default(cls) -> "MessageCategory":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "message.category"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
