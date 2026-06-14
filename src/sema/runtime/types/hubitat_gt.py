from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType


class HubitatGt(SemaType):
    """Sema: https://schemas.electricity.works/types/hubitat.gt/000"""

    host: str
    maker_api_id: StrictInt
    access_token: str
    mac_address: str
    web_listen_enabled: bool
    type_name: Literal["hubitat.gt"] = "hubitat.gt"
    version: Literal["000"] = "000"
