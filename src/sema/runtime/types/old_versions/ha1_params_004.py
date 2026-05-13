from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_005 import Ha1Params005


class Ha1Params004(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/004"""

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
    version: str = '004'

    def upgrade(self) -> Ha1Params005:
        """
        - CopIntercept: add as optional
        - CopOatCoeff: add as optional
        - CopLwtCoeff: add as optional
        - CopMin: add as optional
        - CopMinOatF: add as optional
        """
        data = self.model_dump()
        data["version"] = "005"
        return Ha1Params005.model_validate(data)
