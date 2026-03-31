from typing import Literal

from pydantic import PositiveInt

from sema.registry.base import SemaType
from sema.registry.property_format import LeftRightDot, UTCMilliseconds, UTCSeconds, UUID4Str
from sema.registry.types.channel_readings import ChannelReadings
from sema.registry.types.machine_states import MachineStates
from sema.registry.types.old_versions.fsm_full_report_000 import FsmFullReport000


class Report002(SemaType):
    """Sema: https://schemas.electricity.works/types/report/002"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    about_g_node_alias: LeftRightDot
    slot_start_unix_s: UTCSeconds
    slot_duration_s: PositiveInt
    channel_reading_list: list[ChannelReadings]
    state_list: list[MachineStates]
    fsm_report_list: list[FsmFullReport000]
    message_created_ms: UTCMilliseconds
    id: UUID4Str
    type_name: Literal["report"] = "report"
    version: str = "002"
