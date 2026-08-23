from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.price_quantity_unitless import PriceQuantityUnitless


class PriceQuantityUnitless000(SemaType):
    """Sema: https://schemas.electricity.works/types/price.quantity.unitless/000"""

    price_times1000: StrictInt
    quantity_times1000: StrictInt
    type_name: Literal["price.quantity.unitless"] = "price.quantity.unitless"
    version: Literal["000"] = "000"

    def upgrade(self) -> "PriceQuantityUnitless":
        """
        Rename PriceTimes1000/QuantityTimes1000 to PriceX1000/QuantityX1000.
        """
        data = self.model_dump()
        data["price_x1000"] = data.pop("price_times1000")
        data["quantity_x1000"] = data.pop("quantity_times1000")
        data["version"] = "001"
        return PriceQuantityUnitless.model_validate(data)
