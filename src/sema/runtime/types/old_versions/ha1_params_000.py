from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_001 import Ha1Params001


class Ha1Params000(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/000"""

    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: StrictFloat
    intermediate_rswt_f: StrictInt
    dd_power_kw: StrictFloat
    dd_rswt_f: StrictInt
    dd_delta_t_f: StrictInt
    hp_max_kw_th: StrictFloat
    type_name: Literal["ha1.params"] = "ha1.params"
    version: Literal["000"] = "000"

    def upgrade(self) -> Ha1Params001:
        """- MaxEwtF: add"""
        raise SemaType.upgrade_requires_context(
            "Ha1Params000 cannot be upgraded to "
            "Ha1Params001 without context: v001 adds the "
            "required MaxEwtF, absent from a v000 message and which SHALL NOT be "
            "fabricated."
        )
