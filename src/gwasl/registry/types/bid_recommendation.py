from typing import Literal, Self

from pydantic import model_validator

from gwasl.registry.base import SemaType
from gwasl.registry.enums import MarketPriceUnit, MarketQuantityUnit
from gwasl.registry.property_format import LeftRightDot, MarketSlotName
from gwasl.registry.types.price_quantity_unitless import PriceQuantityUnitless


class BidRecommendation(SemaType):
    bidder_alias: LeftRightDot
    market_slot_name: MarketSlotName
    pq_pairs: list[PriceQuantityUnitless]
    injection_is_positive: bool
    price_unit: MarketPriceUnit
    quantity_unit: MarketQuantityUnit
    type_name: Literal["bid.recommendation"] = "bid.recommendation"
    version: str = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: PqPairs PriceMax matches MarketType.
        There is a GridWorks global list of MarketTypes (a GridWorks type), identified by
        their MarketTypeNames (a GridWorks enum).  The MarketType has a PriceMax, which
        must be the first price of the first PriceQuantity pair in PqPairs.
        """
        # Implement check for axiom 1"
        return self

