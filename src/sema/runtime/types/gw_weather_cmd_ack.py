from typing import Literal
from sema.runtime.base import SemaType


class GwWeatherCmdAck(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.cmd.ack/000"""

    command_hash: str
    type_name: Literal["gw.weather.cmd.ack"] = "gw.weather.cmd.ack"
    version: Literal["000"] = "000"
