from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.send_layout import SendLayout


class SendLayout000(SemaType):
    """Sema: https://schemas.electricity.works/types/send.layout/000"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    type_name: Literal["send.layout"] = "send.layout"
    version: Literal["000"] = "000"

    def upgrade(self) -> SendLayout:
        """
        - FromName: remove
        - ToName: remove
        - MessageCreatedMs: add
        """
        raise ValueError(
            "SendLayout000 cannot be upgraded to "
            "SendLayout without the source message context "
            "needed to supply MessageCreatedMs."
        )
