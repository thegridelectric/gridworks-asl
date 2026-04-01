from typing import Literal, Optional
from sema.runtime.codec import SemaType
from sema.runtime.enums import Gw0RepresentationStatus

class Gw0HouseStatus(SemaType):
    status: Gw0RepresentationStatus
    message: Optional[str] = None
    acked: Optional[bool] = None
    acked_by: Optional[str] = None
    acked_at: Optional[str] = None
    type_name: Literal["gw0.house.status"] = "gw0.house.status"
    version: Literal["000"] = "000"