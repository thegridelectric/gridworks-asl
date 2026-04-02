from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1EmissionMethod(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.emission.method/000"""

    OnTrigger = auto()
    Periodic = auto()
    AsyncAndPeriodic = auto()

    @classmethod
    def default(cls) -> "Gw1EmissionMethod":
        return cls.OnTrigger

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.emission.method"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
