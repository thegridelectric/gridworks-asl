from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_002 import Ha1Params002


class Ha1Params001(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/001"""

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
    type_name: Literal["ha1.params"] = "ha1.params"
    version: Literal["001"] = "001"

    def upgrade(self) -> Ha1Params002:
        """- LoadOverestimationPercent: add"""
        raise SemaType.upgrade_requires_context(
            "Ha1Params001 cannot be upgraded to "
            "Ha1Params002 without context: v002 adds the "
            "required LoadOverestimationPercent field, absent from a v001 "
            "message (which predates the field) and which SHALL NOT be fabricated."
        )
