from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import PositiveInt


class HeatingCurve(SemaType):
    """Sema: https://schemas.electricity.works/types/heating.curve/000"""

    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: PositiveFloat
    intermediate_rswt_f: PositiveInt
    dd_power_kw: PositiveFloat
    dd_rswt_f: PositiveInt
    dd_delta_t_f: PositiveInt
    max_ewt_f: PositiveInt
    type_name: Literal["heating.curve"] = "heating.curve"
    version: Literal["000"] = "000"
