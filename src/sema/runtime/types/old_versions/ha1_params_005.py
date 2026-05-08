from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.ha1_params import Ha1Params


class Ha1Params005(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/005"""

    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: StrictFloat
    intermediate_rswt_f: StrictInt
    dd_power_kw: StrictFloat
    dd_rswt_f: StrictInt
    dd_delta_t_f: StrictInt
    hp_max_kw_th: StrictFloat
    max_ewt_f: StrictInt
    load_overestimation_percent: StrictInt
    cop_intercept: StrictFloat | None = None
    cop_oat_coeff: StrictFloat | None = None
    cop_lwt_coeff: StrictFloat | None = None
    cop_min: StrictFloat | None = None
    cop_min_oat_f: StrictFloat | None = None
    type_name: Literal["ha1.params"] = "ha1.params"
    version: str = '005'

    def upgrade(self) -> Ha1Params:
        """
        - HpMaxKwEl: add as optional
        - HpMaxKwTh: required -> optional
        - HpTurnOnMinutes: add
        - VersioningStrategy: string -> literal
        """
        data = self.model_dump()
        data["hp_turn_on_minutes"] = 12
        data["version"] = "006"
        return Ha1Params.model_validate(data)
