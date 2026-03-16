from enum import auto
from typing import List

from sema.registry.enums.gw_str_enum import SemaEnum


class GNodeStatus(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/g.node.status/000 
    """
    Pending = auto()
    Active = auto()
    PermanentlyDeactivated = auto()
    Suspended = auto()

    @classmethod
    def default(cls) -> "GNodeStatus":
        return cls.Pending

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.status"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
