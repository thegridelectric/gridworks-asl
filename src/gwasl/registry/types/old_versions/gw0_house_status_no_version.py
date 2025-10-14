from typing import Literal, Optional
from gbo.asl.codec import AslType
from gbo.asl.types import HouseStatus

class HouseStatusNoVersion(AslType):
    status: str
    message: Optional[str] = None
    acked: Optional[bool] = None
    acked_by: Optional[str] = None
    acked_at: Optional[str] = None
    type_name: Literal["gw0.house.status"] = "gw0.house.status"


    def to_latest(self) -> "HouseStatus":
        """Convert to the latest version."""
        # status becomes a RepresentationStatus enum
        return HouseStatus.from_dict(self.to_dict())