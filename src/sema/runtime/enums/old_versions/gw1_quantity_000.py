from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1Quantity000(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.quantity/000"""

    Unknown = auto()
    Unitless = auto()
    Power = auto()
    Energy = auto()
    Temperature = auto()
    FlowRate = auto()
    Volume = auto()
    Voltage = auto()
    Current = auto()
    Percent = auto()
    Frequency = auto()

    @classmethod
    def default(cls) -> "Gw1Quantity000":
        return cls.Unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.quantity"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
