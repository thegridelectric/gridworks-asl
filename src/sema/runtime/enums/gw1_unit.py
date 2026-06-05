from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1Unit(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.unit/002"""

    Unknown = auto()
    Unitless = auto()
    FahrenheitX100 = auto()
    Watts = auto()
    WattHours = auto()
    Gallons = auto()
    GpmX100 = auto()
    Seconds = auto()
    SecondsX10 = auto()
    Milliseconds = auto()
    DollarsX1000 = auto()
    MilesPerHourX1000 = auto()
    KilowattHoursX1000 = auto()

    @classmethod
    def default(cls) -> "Gw1Unit":
        return cls.Unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.unit"

    @classmethod
    def enum_version(cls) -> str:
        return "002"
