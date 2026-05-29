from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class GwGNodeClass(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw.g.node.class/000"""

    Unknown = auto()
    TerminalAsset = auto()
    ConnectivityNode = auto()
    LeafTransactiveNode = auto()
    MarketMaker = auto()
    Scada = auto()
    PriceForecastService = auto()
    WeatherForecastService = auto()

    @classmethod
    def default(cls) -> "GwGNodeClass":
        return cls.Unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw.g.node.class"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
