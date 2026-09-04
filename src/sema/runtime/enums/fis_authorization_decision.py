from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class FisAuthorizationDecision(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/fis.authorization.decision/000"""

    Authorized = auto()
    Denied = auto()

    @classmethod
    def default(cls) -> "FisAuthorizationDecision":
        return cls.Denied

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "fis.authorization.decision"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
