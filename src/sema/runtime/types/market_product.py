from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UUID4Str


class MarketProduct(SemaType):
    """Sema: https://schemas.electricity.works/types/market.product/000"""

    market_product_id: UUID4Str
    product_name_enum: LeftRightDot
    name: str
    type_name: Literal["market.product"] = "market.product"
    version: Literal["000"] = "000"
