from typing import Literal
from pydantic import ConfigDict, StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import MarketPriceUnit
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.flo_params_house0_002 import FloParamsHouse0002


class FloParamsHouse0001(SemaType):
    """Sema: https://schemas.electricity.works/types/flo.params.house0/001"""

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
    buffer_available_kwh: StrictFloat | None = None
    house_available_kwh: StrictFloat | None = None
    cop_intercept: StrictFloat
    cop_oat_coeff: StrictFloat
    cop_min: StrictFloat
    cop_min_oat_f: StrictFloat
    cop_lwt_coeff: StrictFloat
    initial_top_temp_f: StrictInt
    initial_bottom_temp_f: StrictInt | None = None
    initial_thermocline: StrictInt
    hp_is_off: bool
    hp_turn_on_minutes: StrictInt
    lmp_forecast: list[StrictFloat] | None = None
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
    discharging_dd_delta_t_f: StrictInt | None = None
    price_unit: MarketPriceUnit
    params_generated_s: UTCSeconds
    type_name: Literal["flo.params.house0"] = "flo.params.house0"
    version: Literal["001"] = "001"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> FloParamsHouse0002:
        """
        - FloAlias: add
        - FloGitCommit: add
        - BufferAvailableKwh: optional -> required
        - HouseAvailableKwh: optional -> required
        - InitialBottomTempF: optional -> required
        """
        raise SemaType.upgrade_requires_context(
            "FloParamsHouse0001 cannot be upgraded to "
            "FloParamsHouse0002 without context: v002 makes "
            "BufferAvailableKwh, HouseAvailableKwh and InitialBottomTempF "
            "required, but the earliest v001 wire shapes omit them, and they "
            "SHALL NOT be fabricated."
        )
