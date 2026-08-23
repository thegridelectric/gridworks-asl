from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.machine_states import MachineStates
from sema.runtime.types.single_reading import SingleReading
from sema.runtime.types.snapshot_spaceheat import SnapshotSpaceheat


class SnapshotSpaceheat002(SemaType):
    """Sema: https://schemas.electricity.works/types/snapshot.spaceheat/002"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    snapshot_time_unix_ms: UTCMilliseconds
    latest_reading_list: list[SingleReading]
    latest_state_list: list[MachineStates]
    type_name: Literal["snapshot.spaceheat"] = "snapshot.spaceheat"
    version: Literal["002"] = "002"

    def upgrade(self) -> SnapshotSpaceheat:
        """LatestStateList element: machine.states -> single.machine.state (one state per entry, adds Cause; drops the parallel StateList/UnixMsList arrays). Type moved from gwproto to scada."""
        raise SemaType.upgrade_requires_context(
            "snapshot.spaceheat:002 cannot be upgraded to snapshot.spaceheat:003 "
            "without context: v003 replaces each machine.states (parallel "
            "StateList/UnixMsList arrays) with per-state single.machine.state "
            "entries carrying a Cause field absent from v002, which SHALL NOT be "
            "fabricated. JournalKeeper retains v002 messages at their own version."
        )
