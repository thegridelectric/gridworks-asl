from typing import Literal

from pydantic import StrictInt

from gwasl.registry.base import AslType


class PriceQuantityUnitless(AslType):
    price_x1000: StrictInt
    quantity_x1000: StrictInt
    type_name: Literal["price.quantity.unitless"] = "price.quantity.unitless"
    version: Literal["001"] = "001"
