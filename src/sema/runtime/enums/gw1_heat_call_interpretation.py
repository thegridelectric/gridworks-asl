from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1HeatCallInterpretation(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.heat.call.interpretation/000"""

    DigitalZeroIsActive = auto()
    DigitalOneIsActive = auto()
    GreaterThanThreshold = auto()

    @classmethod
    def default(cls) -> "Gw1HeatCallInterpretation":
        return cls.DigitalZeroIsActive

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.heat.call.interpretation"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
