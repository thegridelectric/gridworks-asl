from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.ha1_params import Ha1Params


class ScadaParams(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/005"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    new_params: Ha1Params | None = None
    old_params: Ha1Params | None = None
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["005"] = "005"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))
