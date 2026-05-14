from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.ha1_params_004 import Ha1Params004


class ScadaParams(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/004"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    new_params: Ha1Params004 | None = None
    old_params: Ha1Params004 | None = None
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["004"] = "004"
