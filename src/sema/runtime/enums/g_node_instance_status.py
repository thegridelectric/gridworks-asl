from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class GNodeInstanceStatus(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/g.node.instance.status/000"""

    Active = auto()
    Revoked = auto()
    Ended = auto()

    @classmethod
    def default(cls) -> "GNodeInstanceStatus":
        return cls.Active

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.instance.status"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
