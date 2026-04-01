from enum import auto
from typing import List

from sema.runtime.enums.gw_str_enum import SemaEnum


class GNodeClass(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/g.node.class/000
    """

    Unknown = auto()
    TerminalAsset = auto()
    LeafTransactiveNode = auto()
    ConnectivityNode = auto()
    MarketMaker = auto()
    Scada = auto()
    AggregatedTNode = auto()
    PriceForecastService = auto()
    WeatherForecastService = auto()
    TimeCoordinator = auto()

    @classmethod
    def default(cls) -> "GNodeClass":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.class"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
