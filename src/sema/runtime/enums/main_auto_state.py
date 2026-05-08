from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class MainAutoState(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/main.auto.state/001"""

    LocalControl = auto()
    LeafTransactiveNode = auto()
    Dormant = auto()

    @classmethod
    def default(cls) -> "MainAutoState":
        return cls.LocalControl

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "main.auto.state"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
