from typing import Literal, Optional
from gwasl.registry.codec import SemaType

class Gw0HouseContact(SemaType):
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type_name: Literal["gw0.house.contact"] = "gw0.house.contact"