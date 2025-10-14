from typing import Literal, Optional
from gwasl.registry.codec import AslType
from gwasl.registry.enums import Gw0RepresentationStatus

class Gw0HouseStatus(AslType):
    status: Gw0RepresentationStatus
    message: Optional[str] = None
    acked: Optional[bool] = None
    acked_by: Optional[str] = None
    acked_at: Optional[str] = None
    type_name: Literal["gw0.house.status"] = "gw0.house.status"
    version: Literal["000"] = "000"