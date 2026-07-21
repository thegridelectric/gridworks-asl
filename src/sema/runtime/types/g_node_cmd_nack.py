from typing import Literal
from sema.runtime.base import SemaType


class GNodeCmdNack(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.cmd.nack/000"""

    command_hash: str
    reason: str
    type_name: Literal["g.node.cmd.nack"] = "g.node.cmd.nack"
    version: Literal["000"] = "000"
