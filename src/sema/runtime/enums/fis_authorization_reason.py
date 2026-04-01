from enum import auto
from typing import List

from sema.runtime.enums.gw_str_enum import SemaEnum


class FisAuthorizationReason(SemaEnum):
    """
    Sema:
    https://schemas.electricity.works/enums/fis.authorization.reason/000
    (Not yet published)
    """

    NewInstance = auto()
    IdempotentReconnect = auto()
    SupersededPrevious = auto()
    MalformedRequest = auto()
    UnknownGNode = auto()
    InactiveGNode = auto()
    AliasMismatch = auto()
    ClassMismatch = auto()
    InstanceRevoked = auto()
    SecurityViolation = auto()

    @classmethod
    def default(cls) -> "FisAuthorizationReason":
        return cls.SecurityViolation

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "fis.authorization.reason"

    @classmethod
    def enum_version(cls) -> str:
        return "000"