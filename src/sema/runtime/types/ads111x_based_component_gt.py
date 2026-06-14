from typing import Literal
from pydantic import StrictFloat
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.ads_channel_config import AdsChannelConfig


class Ads111xBasedComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/ads111x.based.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[AdsChannelConfig]
    open_voltage_by_ads: list[StrictFloat]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["ads111x.based.component.gt"] = "ads111x.based.component.gt"
    version: Literal["000"] = "000"
