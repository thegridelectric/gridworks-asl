from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class GwWeatherForecastFidelity(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw.weather.forecast.fidelity/000"""

    Unknown = auto()
    Live = auto()
    Stored = auto()
    SeasonalTemplate = auto()

    @classmethod
    def default(cls) -> "GwWeatherForecastFidelity":
        return cls.Unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw.weather.forecast.fidelity"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
