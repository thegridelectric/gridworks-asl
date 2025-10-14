from typing import Literal

from gwasl.registry import AslType
from gwasl.registry.enums import RelayClosedOrOpen
from gwasl.registry.property_format import SpaceheatName


class RcoRelayReading(AslType):
    name: SpaceheatName
    value: RelayClosedOrOpen
    type_name: Literal["rco.relay.reading"] = "rco.relay.reading"
