from typing import Literal
from pydantic import ConfigDict, StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import MarketPriceUnit
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.flo_params_house0_004 import FloParamsHouse0004


class FloParamsHouse0003(SemaType):
    """Sema: https://schemas.electricity.works/types/flo.params.house0/003"""

    g_node_alias: LeftRightDot
    flo_params_uid: UUID4Str
    timezone_str: str
    start_unix_s: UTCSeconds
    num_layers: PositiveInt
    horizon_hours: PositiveInt
    storage_volume_gallons: PositiveInt
    storage_losses_percent: StrictFloat
    hp_min_elec_kw: StrictFloat
    hp_max_elec_kw: StrictFloat
    buffer_available_kwh: StrictFloat
    house_available_kwh: StrictFloat
    cop_intercept: StrictFloat
    cop_oat_coeff: StrictFloat
    cop_min: StrictFloat
    cop_min_oat_f: StrictFloat
    cop_lwt_coeff: StrictFloat
    initial_top_temp_f: StrictInt
    initial_middle_temp_f: StrictInt
    initial_bottom_temp_f: StrictInt
    hp_is_off: bool
    hp_turn_on_minutes: StrictInt
    lmp_forecast: list[StrictFloat] | None = None
    initial_thermocline1: StrictInt
    initial_thermocline2: StrictInt
    dist_price_forecast: list[StrictFloat] | None = None
    reg_price_forecast: list[StrictFloat] | None = None
    price_forecast_uid: UUID4Str
    oat_forecast_f: list[StrictFloat] | None = None
    wind_speed_forecast_mph: list[StrictFloat] | None = None
    weather_uid: UUID4Str
    alpha_times10: StrictInt
    beta_times100: StrictInt
    gamma_ex6: StrictInt
    intermediate_power_kw: StrictFloat
    intermediate_rswt_f: StrictInt
    dd_power_kw: StrictFloat
    dd_rswt_f: StrictInt
    dd_delta_t_f: StrictInt
    max_ewt_f: StrictInt
    price_unit: MarketPriceUnit
    params_generated_s: UTCSeconds
    flo_alias: str | None = None
    flo_git_commit: str | None = None
    constant_delta_t: StrictInt | None = None
    type_name: Literal["flo.params.house0"] = "flo.params.house0"
    version: Literal["003"] = "003"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> FloParamsHouse0004:
        """
        - FloAlias: remove
        - FloGitCommit: remove
        - ConstantDeltaT: optional -> required
        """
        data = self.model_dump()
        data.pop("flo_alias", None)
        data.pop("flo_git_commit", None)
        if data.get("constant_delta_t") is None:
            data["constant_delta_t"] = 20
        data["version"] = "004"
        return FloParamsHouse0004.model_validate(data)
