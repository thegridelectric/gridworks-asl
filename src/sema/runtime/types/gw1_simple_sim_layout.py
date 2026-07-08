from typing import Literal
from sema.runtime.base import SemaType


class Gw1SimpleSimLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.simple.sim.layout/000"""

    type_name: Literal["gw1.simple.sim.layout"] = "gw1.simple.sim.layout"
    version: Literal["000"] = "000"
