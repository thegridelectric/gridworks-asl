from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.types.ha1_params import Ha1Params as Ha1Params006


class Ha1Params005(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/005"""

    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: float
    intermediate_rswt_f: StrictInt
    dd_power_kw: float
    dd_rswt_f: StrictInt
    dd_delta_t_f: StrictInt
    hp_max_kw_th: float
    max_ewt_f: StrictInt
    load_overestimation_percent: StrictInt
    cop_intercept: float | None = None
    cop_oat_coeff: float | None = None
    cop_lwt_coeff: float | None = None
    cop_min: float | None = None
    cop_min_oat_f: float | None = None
    type_name: str = "ha1.params"
    version: str = "005"

    def upgrade(self) -> Ha1Params006:
        """
        005 -> 006:
        - HpMaxKwTh -> HpMaxKwEl
        - HpTurnOnMinutes: add
        """
        data = self.model_dump()
        data["hp_max_kw_el"] = data.pop("hp_max_kw_th") / 2
        data["hp_turn_on_minutes"] = 15
        data["version"] = "006"
        return Ha1Params006.model_validate(data)
