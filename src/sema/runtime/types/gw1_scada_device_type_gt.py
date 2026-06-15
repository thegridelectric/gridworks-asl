from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt


class Gw1ScadaDeviceTypeGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.scada.device.type.gt/000"""

    device_type: PascalCase
    display_name: str | None = None
    min_poll_period_ms: PositiveInt | None = None
    type_name: Literal["gw1.scada.device.type.gt"] = "gw1.scada.device.type.gt"
    version: Literal["000"] = "000"
