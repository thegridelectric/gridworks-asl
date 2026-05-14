from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot


class KeyparamChangeLog(SemaType):
    """Sema: https://schemas.electricity.works/types/keyparam.change.log/000"""

    about_node_alias: LeftRightDot
    change_time_utc: str
    author: str
    param_name: str
    description: str
    kind: str
    type_name: Literal["keyparam.change.log"] = "keyparam.change.log"
    version: Literal["000"] = "000"
