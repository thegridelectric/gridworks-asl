from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_004 import Ha1Params004


class Ha1Params003(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/003"""

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
    strat_boss_dist010: StrictInt
    type_name: Literal["ha1.params"] = "ha1.params"
    version: Literal["003"] = "003"

    def upgrade(self) -> Ha1Params004:
        """Baseline runtime version (no prior version tracked)."""
        data = self.model_dump()
        data.pop("strat_boss_dist010", None)
        data["version"] = "004"
        return Ha1Params004.model_validate(data)
