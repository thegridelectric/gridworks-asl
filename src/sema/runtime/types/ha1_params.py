from pydantic import StrictInt

from sema.runtime.base import SemaType


class Ha1Params(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/006"""

    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: float
    intermediate_rswt_f: StrictInt
    dd_power_kw: float
    dd_rswt_f: StrictInt
    dd_delta_t_f: StrictInt
    hp_max_kw_el: float | None = None
    hp_max_kw_th: float | None = None
    max_ewt_f: StrictInt
    load_overestimation_percent: StrictInt
    cop_intercept: float | None = None
    cop_oat_coeff: float | None = None
    cop_lwt_coeff: float | None = None
    cop_min: float | None = None
    cop_min_oat_f: float | None = None
    hp_turn_on_minutes: StrictInt = 12
    type_name: str = "ha1.params"
    version: str = "006"
