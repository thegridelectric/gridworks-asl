from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.snapshot_spaceheat_002 import SnapshotSpaceheat002
from sema.runtime.types.single_reading import SingleReading


class SnapshotSpaceheat001(SemaType):
    """Sema: https://schemas.electricity.works/types/snapshot.spaceheat/001"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    snapshot_time_unix_ms: UTCMilliseconds
    latest_reading_list: list[SingleReading]
    type_name: Literal["snapshot.spaceheat"] = "snapshot.spaceheat"
    version: Literal["001"] = "001"

    def upgrade(self) -> SnapshotSpaceheat002:
        """- LatestStateList: add (machine.states:000, parallel StateList / UnixMsList arrays per machine)"""
        raise SemaType.upgrade_requires_context(
            "snapshot.spaceheat:001 cannot be upgraded to snapshot.spaceheat:002 "
            "without context: v002 adds the required LatestStateList, absent "
            "from a v001 message and which SHALL NOT be fabricated. "
            "JournalKeeper retains v001 messages at their own version."
        )
