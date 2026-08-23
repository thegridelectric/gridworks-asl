from typing import Literal
from pydantic import ConfigDict, StrictFloat, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import MarketPriceUnit
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.flo_params_house0_001 import FloParamsHouse0001


class FloParamsHouse0000(SemaType):
    """Sema: https://schemas.electricity.works/types/flo.params.house0/000"""

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
    cop_intercept: StrictFloat
    cop_oat_coeff: StrictFloat
    cop_lwt_coeff: StrictFloat
    initial_top_temp_f: StrictInt
    initial_thermocline: StrictInt
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
    price_unit: MarketPriceUnit
    params_generated_s: UTCSeconds
    type_name: Literal["flo.params.house0"] = "flo.params.house0"
    version: Literal["000"] = "000"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> FloParamsHouse0001:
        """
        - CopMin: add
        - CopMinOatF: add
        - HpIsOff: add
        - HpTurnOnMinutes: add
        """
        raise SemaType.upgrade_requires_context(
            "FloParamsHouse0000 cannot be upgraded to "
            "FloParamsHouse0001 without context: v001 adds "
            "the required CopMin, CopMinOatF, HpIsOff and HpTurnOnMinutes, absent "
            "from a v000 message and which SHALL NOT be fabricated."
        )
