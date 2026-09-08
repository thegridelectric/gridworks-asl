from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import NonEmptyString


class GwCommandTransition(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.command.transition/000"""

    event: NonEmptyString
    to_state: NonEmptyString
    type_name: Literal["gw.command.transition"] = "gw.command.transition"
    version: Literal["000"] = "000"
