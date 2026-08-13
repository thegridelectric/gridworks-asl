from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1ActuationAuthority
from sema.runtime.enums import Gw1SeasonalStorageMode
from sema.runtime.enums import Gw1ServiceMode
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PositiveInt
from sema.runtime.types.capture_tuning import CaptureTuning
from sema.runtime.types.cop_curve import CopCurve
from sema.runtime.types.heating_curve import HeatingCurve


class GwHouse0OperationalParams(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.house0.operational.params/000"""

    scada_alias: LeftRightDot
    capture_tuning_list: list[CaptureTuning]
    actuation_authority: Gw1ActuationAuthority
    service_mode: Gw1ServiceMode
    seasonal_storage_mode: Gw1SeasonalStorageMode
    cop_curve: CopCurve
    heating_curve: HeatingCurve
    hp_turn_on_minutes: PositiveInt
    short_cycle_buffer: bool
    load_overestimation_percent: NonNegativeInt
    oil_boiler_backup: bool
    horizon_hours: PositiveInt
    type_name: Literal["gw.house0.operational.params"] = "gw.house0.operational.params"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwHouse0OperationalParams":
        """
        Axiom 1: CaptureTuningChannelUniqueness
        ChannelName SHALL be unique across CaptureTuningList.
        """
        names = [ct.channel_name for ct in self.capture_tuning_list]
        if len(names) != len(set(names)):
            raise ValueError(
                "Axiom 1 (CaptureTuningChannelUniqueness) failed: ChannelName "
                "must be unique across CaptureTuningList."
            )
        return self
