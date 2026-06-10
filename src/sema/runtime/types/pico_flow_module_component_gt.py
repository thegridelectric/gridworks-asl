from typing import Literal
from pydantic import StrictFloat, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GpmFromHzMethod
from sema.runtime.enums import HzCalcMethod
from sema.runtime.enums.old_versions.spaceheat_make_model_003 import (
    SpaceheatMakeModel003,
)
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_config import ChannelConfig


class PicoFlowModuleComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.flow.module.component.gt/000"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    enabled: bool
    serial_number: str
    flow_node_name: SpaceheatName
    flow_meter_type: SpaceheatMakeModel003
    hz_calc_method: HzCalcMethod
    gpm_from_hz_method: GpmFromHzMethod
    constant_gallons_per_tick: StrictFloat
    send_hz: bool
    send_gallons: bool
    send_tick_lists: bool
    no_flow_ms: StrictInt
    async_capture_threshold_gpm_times100: StrictInt
    publish_empty_ticklist_after_s: StrictInt | None = None
    publish_any_ticklist_after_s: StrictInt | None = None
    publish_ticklist_period_s: StrictInt | None = None
    publish_ticklist_length: StrictInt | None = None
    exp_alpha: StrictFloat | None = None
    cutoff_frequency: StrictFloat | None = None
    type_name: Literal["pico.flow.module.component.gt"] = (
        "pico.flow.module.component.gt"
    )
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "PicoFlowModuleComponentGt":
        """
        Axiom 1: HwUidPattern
        If HwUid is present, it SHALL match the pattern pico_xxxxxx where xxxxxx consists of six
        lowercase hexadecimal characters.
        """
        import re

        if self.hw_uid is not None and not re.fullmatch(
            r"pico_[0-9a-f]{6}", self.hw_uid
        ):
            raise ValueError(
                "Axiom 1 failed: hw_uid must match pico_xxxxxx with lowercase hex."
            )
        return self
