from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class FisAuthorizationReason(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/fis.authorization.reason/000"""

    MalformedRequest = auto()
    PrincipalNotFound = auto()
    PrincipalSuspended = auto()
    RunOutsideUniverse = auto()
    NotInRegistry = auto()
    AliasMismatch = auto()
    ClassMismatch = auto()
    InstanceRevoked = auto()
    KillUnconfirmed = auto()
    LeaseRace = auto()
    IdempotentReconnect = auto()
    Superseded = auto()

    @classmethod
    def default(cls) -> "FisAuthorizationReason":
        return cls.MalformedRequest

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "fis.authorization.reason"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
