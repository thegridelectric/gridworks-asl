from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.scada_params_001 import ScadaParams001


class ScadaParams000(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/000"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["000"] = "000"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> ScadaParams001:
        """Earliest params-bearing scada.params, back-filled from S3 evidence. NewParams/OldParams carry an ha1.params:000 object (nine-field shape)."""
        raise SemaType.upgrade_requires_context(
            "scada.params:000 cannot be upgraded to scada.params:001 without "
            "context: v000 is a free-form param-setter whose ad-hoc fields do "
            "not map deterministically to v001's structured NewParams/OldParams "
            "ha1.params objects. JournalKeeper retains v000 messages at their "
            "own version."
        )
