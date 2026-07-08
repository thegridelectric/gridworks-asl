from typing import Literal
from pydantic import StrictFloat
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName


class Gw1HvacZone(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.hvac.zone/000"""

    name: SpaceheatName
    critical: bool
    kwh_per_deg_f: StrictFloat
    type_name: Literal["gw1.hvac.zone"] = "gw1.hvac.zone"
    version: Literal["000"] = "000"
