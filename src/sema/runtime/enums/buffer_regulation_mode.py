from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class BufferRegulationMode(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/buffer.regulation.mode/000"""

    Normal = auto()
    Tight = auto()

    @classmethod
    def default(cls) -> "BufferRegulationMode":
        return cls.Normal

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "buffer.regulation.mode"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
