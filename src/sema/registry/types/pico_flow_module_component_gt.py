import re
from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.enums.gpm_from_hz_method import GpmFromHzMethod
from sema.registry.enums.hz_calc_method import HzCalcMethod
from sema.registry.enums.spaceheat_make_model import SpaceheatMakeModel
from sema.registry.property_format import UUID4Str, SpaceheatName
from sema.registry.types.channel_config import ChannelConfig


_PICO_HW_UID_PATTERN = re.compile(r"^pico_[0-9a-f]{6}$")


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
    flow_meter_type: SpaceheatMakeModel
    hz_calc_method: HzCalcMethod
    gpm_from_hz_method: GpmFromHzMethod
    constant_gallons_per_tick: float
    send_hz: bool
    send_gallons: bool
    send_tick_lists: bool
    no_flow_ms: int
    async_capture_threshold_gpm_times100: int
    publish_empty_ticklist_after_s: int | None = None
    publish_any_ticklist_after_s: int | None = None
    publish_ticklist_period_s: int | None = None
    publish_ticklist_length: int | None = None
    exp_alpha: float | None = None
    cutoff_frequency: float | None = None
    type_name: Literal["pico.flow.module.component.gt"] = "pico.flow.module.component.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "PicoFlowModuleComponentGt":
        if self.hw_uid is not None and not _PICO_HW_UID_PATTERN.fullmatch(self.hw_uid):
            raise ValueError(
                "Axiom 1 failed: hw_uid must match pico_xxxxxx with lowercase hex."
            )
        return self
