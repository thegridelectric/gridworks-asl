from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import GpmFromHzMethod
from sema.runtime.enums import HzCalcMethod
from sema.runtime.enums import TempCalcMethod
from sema.runtime.enums.old_versions.spaceheat_make_model_007 import (
    SpaceheatMakeModel007,
)
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.channel_config_000 import ChannelConfig000
from sema.runtime.types.pico_btu_meter_component_gt import PicoBtuMeterComponentGt


class PicoBtuMeterComponentGt000(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.btu.meter.component.gt/000"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ChannelConfig000]
    enabled: bool
    serial_number: str
    flow_channel_name: SpaceheatName
    hot_channel_name: SpaceheatName
    cold_channel_name: SpaceheatName
    ct_channel_name: SpaceheatName | None = None
    read_ct_voltage: bool
    send_hz: bool
    flow_meter_type: SpaceheatMakeModel007
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

    def upgrade(self) -> PicoBtuMeterComponentGt:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        - FlowMeterType: spaceheat.make.model enum value -> gw1.device.type value (pascal.case); the device-type enum is articulated by the hardware layout.
        """
        raise SemaType.upgrade_requires_context(
            "PicoBtuMeterComponentGt000 cannot be upgraded to "
            "PicoBtuMeterComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
