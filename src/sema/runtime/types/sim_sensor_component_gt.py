from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str


class SimSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.sensor.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["sim.sensor.component.gt"] = "sim.sensor.component.gt"
    version: Literal["000"] = "000"
