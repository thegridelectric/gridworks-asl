from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.ha1_params_000 import Ha1Params000
from sema.runtime.types.old_versions.scada_params_002 import ScadaParams002


class ScadaParams001(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/001"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    new_params: Ha1Params000 | None = None
    old_params: Ha1Params000 | None = None
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["001"] = "001"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> ScadaParams002:
        """
        - NewParams/OldParams element: ha1.params 000 -> 001/002/003
        """
        raise SemaType.upgrade_requires_context(
            "scada.params:001 cannot be upgraded to scada.params:002 without "
            "context: its NewParams/OldParams upgrade ha1.params 000 -> 001, "
            "which adds the required MaxEwtF that SHALL NOT be fabricated."
        )
