from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import MarketQuantityUnit
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UUID4Str


class MarketProduct(SemaType):
    """Sema: https://schemas.electricity.works/types/market.product/000"""

    market_product_id: UUID4Str
    product_name_enum: LeftRightDot
    name: str
    slot_duration_minutes: StrictInt
    gate_closing_seconds: StrictInt
    quantity_unit: MarketQuantityUnit | None = None
    type_name: Literal["market.product"] = "market.product"
    version: Literal["000"] = "000"
