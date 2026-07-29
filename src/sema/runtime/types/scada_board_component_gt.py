from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str


class ScadaBoardComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.board.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    i2c_address_list: list[NonNegativeInt] | None = None
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["scada.board.component.gt"] = "scada.board.component.gt"
    version: Literal["000"] = "000"
