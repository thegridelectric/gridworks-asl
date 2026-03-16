from enum import auto
from typing import List

from sema.registry.enums.gw_str_enum import SemaEnum


class RecognizedCurrencyUnit(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/recognized.currency.unit/000
    """

    UNKNOWN = auto()
    USD = auto()
    GBP = auto()

    @classmethod
    def default(cls) -> "RecognizedCurrencyUnit":
        return cls.UNKNOWN

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "recognized.currency.unit"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
