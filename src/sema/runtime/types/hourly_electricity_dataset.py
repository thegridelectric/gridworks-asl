from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import UtcIso8601Seconds


class HourlyElectricityDataset(SemaType):
    """Sema: https://schemas.electricity.works/types/hourly.electricity.dataset/000"""

    hour_list: list[UtcIso8601Seconds]
    price_usd_per_kwh_list: list[StrictFloat]
    usage_kwh_list: list[StrictFloat]
    type_name: Literal["hourly.electricity.dataset"] = "hourly.electricity.dataset"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "HourlyElectricityDataset":
        """
        Axiom 1: ArrayLengthAlignment
        The lengths of HourList, PriceUsdPerKwhList, and UsageKwhList shall be equal.
        """
        if len(self.hour_list) != len(self.price_usd_per_kwh_list):
            raise ValueError(
                "Axiom 1 failed: hour_list and price_usd_per_kwh_list must have equal length."
            )
        if len(self.hour_list) != len(self.usage_kwh_list):
            raise ValueError(
                "Axiom 1 failed: hour_list and usage_kwh_list must have equal length."
            )
        return self
