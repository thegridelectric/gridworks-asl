from sema.registry.base import SemaType


class Ha1Params(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/006"""

    alpha_times10: int
    beta_times100: int
    gamma_ex6: int
    intermediate_power_kw: float
    intermediate_rswt_f: int
    dd_power_kw: float
    dd_rswt_f: int
    dd_delta_t_f: int
    hp_max_kw_el: float
    max_ewt_f: int
    load_overestimation_percent: int
    cop_intercept: float
    cop_oat_coeff: float
    cop_lwt_coeff: float
    cop_min: float
    cop_min_oat_f: float
    hp_turn_on_minutes: int = 12
    type_name: str = "ha1.params"
    version: str = "006"
