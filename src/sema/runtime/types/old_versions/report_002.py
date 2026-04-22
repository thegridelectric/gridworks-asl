from typing import Literal

from sema.runtime.base import SemaType
from sema.runtime.property_format import (
    LeftRightDot,
    PositiveInt,
    UTCMilliseconds,
    UTCSeconds,
    UUID4Str,
)
from sema.runtime.types.channel_readings import ChannelReadings
from sema.runtime.types.fsm_full_report import FsmFullReport
from sema.runtime.types.machine_states import MachineStates
from sema.runtime.types.old_versions.fsm_full_report_000 import FsmFullReport000
from sema.runtime.types.report import Report as Report003

class Report002(SemaType):
    """Sema: https://schemas.electricity.works/types/report/002"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    about_g_node_alias: LeftRightDot
    slot_start_unix_s: UTCSeconds
    slot_duration_s: PositiveInt
    channel_reading_list: list[ChannelReadings]
    state_list: list[MachineStates]
    fsm_report_list: list[FsmFullReport000 | FsmFullReport]
    message_created_ms: UTCMilliseconds
    id: UUID4Str
    type_name: Literal["report"] = "report"
    version: str = "002"

    def upgrade(self) -> Report003:
        """
        002 -> 003: FsmReportList[]: fsm.full.report:000|001 -> 001
        """
        data = self.model_dump()
        data["fsm_report_list"] = [
            fsm_report.upgrade() if fsm_report.version == "000" else fsm_report for fsm_report in self.fsm_report_list
        ]
        data["version"] = "003"
        return Report003.model_validate(data)
