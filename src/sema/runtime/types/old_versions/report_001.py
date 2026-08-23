from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_readings import ChannelReadings
from sema.runtime.types.old_versions.fsm_atomic_report_000 import FsmAtomicReport000
from sema.runtime.types.old_versions.fsm_full_report_000 import FsmFullReport000
from sema.runtime.types.old_versions.report_002 import Report002


class Report001(SemaType):
    """Sema: https://schemas.electricity.works/types/report/001"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    about_g_node_alias: LeftRightDot
    slot_start_unix_s: UTCSeconds
    slot_duration_s: PositiveInt
    channel_reading_list: list[ChannelReadings]
    fsm_action_list: list[FsmAtomicReport000]
    fsm_report_list: list[FsmFullReport000]
    message_created_ms: UTCMilliseconds
    id: UUID4Str
    type_name: Literal["report"] = "report"
    version: str = "001"

    def upgrade(self) -> Report002:
        """- StateList: add (machine.states:000)
        - FsmActionList: remove
        - FsmReportList[]: fsm.full.report:000 -> oneOf[000, 001]"""
        raise SemaType.upgrade_requires_context(
            "report:001 cannot be upgraded to report:002 without context: v002 "
            "replaces FsmActionList with the required StateList (machine.states), "
            "not derivable from a v001 message. JournalKeeper retains v001 "
            "messages at their own version."
        )
