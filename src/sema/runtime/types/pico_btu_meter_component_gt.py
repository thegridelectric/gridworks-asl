from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import GpmFromHzMethod
from sema.runtime.enums import HzCalcMethod
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str


class PicoBtuMeterComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.btu.meter.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    enabled: bool
    serial_number: str
    flow_channel_name: SpaceheatName
    hot_channel_name: SpaceheatName
    cold_channel_name: SpaceheatName
    ct_channel_name: SpaceheatName | None = None
    read_ct_voltage: bool
    send_hz: bool
    flow_meter_type: PascalCase
    hz_calc_method: HzCalcMethod
    temp_calc_method: TempCalcMethod
    gpm_from_hz_method: GpmFromHzMethod
    thermistor_beta: StrictInt
    gallons_per_pulse: PositiveFloat
    async_capture_delta_gpm_x100: StrictInt
    async_capture_delta_celsius_x100: StrictInt
    async_capture_delta_ct_volts_x100: StrictInt | None = None
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["pico.btu.meter.component.gt"] = "pico.btu.meter.component.gt"
    version: Literal["000"] = "000"
