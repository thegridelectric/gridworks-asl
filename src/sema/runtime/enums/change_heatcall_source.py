from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class ChangeHeatcallSource(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/change.heatcall.source/000"""

    WallThermostat = auto()
    Scada = auto()

    @classmethod
    def default(cls) -> "ChangeHeatcallSource":
        return cls.WallThermostat

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "change.heatcall.source"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
