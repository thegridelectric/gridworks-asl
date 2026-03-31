from enum import auto

from sema.registry.enums.gw_str_enum import SemaEnum


class Gw1SeasonalStorageMode(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.seasonal.storage.mode/000"""

    AllTanks = auto()
    BufferOnly = auto()

    @classmethod
    def default(cls) -> "Gw1SeasonalStorageMode":
        return cls.AllTanks

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.seasonal.storage.mode"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
