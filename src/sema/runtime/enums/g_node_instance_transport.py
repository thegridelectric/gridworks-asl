from enum import auto
from typing import List

from sema.runtime.enums.gw_str_enum import SemaEnum


class GNodeInstanceTransport(SemaEnum):
    """
    Sema: https://schemas.electricity.works/enums/g.node.instance.transport/000
    """

    RabbitAmqp = auto()
    RabbitMqtt = auto()

    @classmethod
    def default(cls) -> "GNodeInstanceTransport":
        return cls.RabbitAmqp

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.instance.transport"

    @classmethod
    def enum_version(cls) -> str:
        return "000"