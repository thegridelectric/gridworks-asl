from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str


class SimReady(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.ready/000"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    time_unix_s: UTCSeconds
    type_name: Literal["sim.ready"] = "sim.ready"
    version: Literal["000"] = "000"
