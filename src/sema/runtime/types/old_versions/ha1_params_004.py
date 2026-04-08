from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.types.old_versions.ha1_params_005 import Ha1Params005


class Ha1Params004(SemaType):
    """Sema: https://schemas.electricity.works/types/ha1.params/004"""

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
    type_name: str = "ha1.params"
    version: str = "004"

    def upgrade(self) -> Ha1Params005:
        """
        004 -> 005:
        - CopModelCoefficients: add
        - MinimumOperatingCopParameters: add
        """
        data = self.model_dump()
        data["cop_intercept"] = 1.8
        data["cop_oat_coeff"] = 0.012
        data["cop_lwt_coeff"] = 0.0
        data["cop_min"] = 1.8
        data["cop_min_oat_f"] = 0.0
        data["version"] = "005"
        return Ha1Params005.model_validate(data)
