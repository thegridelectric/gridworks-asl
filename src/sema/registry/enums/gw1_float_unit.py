from enum import auto

from sema.registry.enums.gw_str_enum import SemaEnum


class Gw1FloatUnit(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.float.unit/000"""

    Seconds = auto()
    Milliseconds = auto()
    Fahrenheit = auto()
    Celsius = auto()
    Watts = auto()
    WattHours = auto()
    Gallons = auto()
    GallonsPerMinute = auto()

    @classmethod
    def default(cls) -> "Gw1FloatUnit":
        return cls.Watts

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.float.unit"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
