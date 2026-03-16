from typing import Literal, Self

import pendulum
from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.enums import MarketCategory, MarketPriceUnit, MarketTypeName
from sema.registry.property_format import (
    LeftRightDot,
    MarketName,
)


class Market(SemaType):
    name: MarketName
    market_type_name: MarketTypeName
    p_node_alias: LeftRightDot
    category: MarketCategory
    unit: MarketPriceUnit
    timezone: str
    type_name: Literal["market"] = "market"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom : Name Derived from MarketTypeName, PNodeAlias and Category.
        Name = f"x.{MarketTypeName}.{PNode}" where x = e if category is energy, d if distribution, r if regulation.
        """
        suffix = f"{self.market_type_name}.{self.p_node_alias}"
        name_parts = self.name.split(".")
        remainder = ".".join(name_parts[1:])
        if suffix != remainder:
            raise ValueError(f"name {self.name} does not match {suffix}!")
        category_shorthand = name_parts[0]
        if (
            (self.category == MarketCategory.Energy and category_shorthand != "e")
            or (
                self.category == MarketCategory.Distribution
                and category_shorthand != "d"
            )
            or (
                self.category == MarketCategory.Regulation and category_shorthand != "r"
            )
        ):
            raise ValueError(f"name {self.name} does not match {self.category}")

        return self

    @model_validator(mode='after')
    def check_axiom_2(self) -> Self:
        """Axiom 2: timezone must be a valid timezone recognized by pendulum"""
        try:
            pendulum.timezone(self.timezone)
        except Exception as e:
            raise ValueError(f"'{self.timezone}' is not a valid timezone. Examples: 'America/New_York', 'UTC', 'US/Eastern'") from e
        return self
