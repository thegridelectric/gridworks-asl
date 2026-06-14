from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.dfr_config import DfrConfig


class DfrComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/dfr.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[DfrConfig]
    i2c_address_list: list[PositiveInt]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["dfr.component.gt"] = "dfr.component.gt"
    version: Literal["000"] = "000"
