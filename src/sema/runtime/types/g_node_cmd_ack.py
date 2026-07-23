from typing import Literal
from sema.runtime.base import SemaType


class GNodeCmdAck(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.cmd.ack/000"""

    command_hash: str
    type_name: Literal["g.node.cmd.ack"] = "g.node.cmd.ack"
    version: Literal["000"] = "000"
