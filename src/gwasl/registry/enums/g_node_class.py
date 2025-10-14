from enum import auto
from typing import List

from gw.enums import GwStrEnum


class GNodeClass(GwStrEnum):
    """
    GNode classification used to support message passing based on function.
    Values:
      - GNode: GNode with unspecified action.
      - TerminalAsset: GNode representing the actual physical transactive asset. Can be simulated.
      - Scada: GNode responsible for local data acquisition and control of a TerminalAsset.
      - LeafTransactiveNode: The transactive agent for a TerminalAsset, with authority to enter into 
        Dispatch Contracts with the SCADA.
      - MarketMaker: Manages local constraints and "trues up" existing ISO-level market mechanisms 
        to allow for natural market structures (like sub-metering).
      - PriceService: Service providing price forecasts as a service to LTNs.
      - WeatherService: Service providing weather forecasts as a servivec to LTNs

    For more information:
        - [ASL Definition](https://raw.githubusercontent.com/thegridelectric/gridworks-asl/refs/heads/dev/type_definitions/enums/g.node.class.000.yaml)
        - [GridWorks ASL Docs](https://gridworks-asl.readthedocs.io)
    """

    GNode = auto()
    TerminalAsset = auto()
    Scada = auto()
    LeafTransactiveNode = auto()
    MarketMaker = auto()
    PriceService = auto()
    WeatherService = auto()

    @classmethod
    def default(cls) -> "GNodeClass":
        return cls.GNode

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.class"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
