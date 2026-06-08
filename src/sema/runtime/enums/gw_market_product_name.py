from dataclasses import dataclass
from enum import auto

from sema.runtime.enums.gw_str_enum import StructuredEnum


@dataclass(frozen=True)
class GwMarketProductNameAttrs:
    timeframe: str | None
    slot_minutes: int | None
    gate_minutes: int | None
    quantity_unit: str | None


class GwMarketProductName(StructuredEnum):
    """Sema: https://schemas.electricity.works/enums/gw.market.product.name/000"""

    unknown = auto()
    da60 = auto()
    rt60gate5 = auto()
    rt60gate30 = auto()
    rt60gate30b = auto()
    rt30gate5 = auto()
    rt15gate5 = auto()
    rt5gate5 = auto()

    @classmethod
    def default(cls) -> "GwMarketProductName":
        return cls.unknown

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw.market.product.name"

    @classmethod
    def enum_version(cls) -> str:
        return "000"

    @property
    def attrs(self) -> "GwMarketProductNameAttrs | None":
        return _ATTRS.get(self.value)


_ATTRS: dict[str, GwMarketProductNameAttrs] = {
    'da60': GwMarketProductNameAttrs(timeframe='da', slot_minutes=60, gate_minutes=None, quantity_unit='AvgkWh'),
    'rt60gate5': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=60, gate_minutes=5, quantity_unit='AvgkWh'),
    'rt60gate30': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=60, gate_minutes=30, quantity_unit='AvgkWh'),
    'rt60gate30b': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=60, gate_minutes=30, quantity_unit='AvgkW'),
    'rt30gate5': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=30, gate_minutes=5, quantity_unit='AvgkWh'),
    'rt15gate5': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=15, gate_minutes=5, quantity_unit='AvgkWh'),
    'rt5gate5': GwMarketProductNameAttrs(timeframe='rt', slot_minutes=5, gate_minutes=5, quantity_unit='AvgkWh'),
}
