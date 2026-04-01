from enum import auto
from typing import List

from sema.runtime.enums.gw_str_enum import SemaEnum


class MessageCategorySymbol(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/message.category.symbol/000
    """

    unknown = auto()
    rj = auto()
    rjb = auto()
    gw = auto()
    s = auto()

    @classmethod
    def default(cls) -> "MessageCategorySymbol":
        return cls.unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "message.category.symbol"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
