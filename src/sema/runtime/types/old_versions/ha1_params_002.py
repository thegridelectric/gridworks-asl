from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_003 import Ha1Params003


class Ha1Params002(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/002"""

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
    type_name: Literal["ha1.params"] = "ha1.params"
    version: Literal["002"] = "002"

    def upgrade(self) -> Ha1Params003:
        """- StratBossDist010: add"""
        raise SemaType.upgrade_requires_context(
            "Ha1Params002 cannot be upgraded to "
            "Ha1Params003 without context: v003 adds the "
            "required StratBossDist010 StratBoss parameter, absent from a v002 "
            "message (which predates the field) and which SHALL NOT be fabricated."
        )
