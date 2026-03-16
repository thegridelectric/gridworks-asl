from typing import Literal

from sema.registry import SemaType
from sema.registry.enums import RelayClosedOrOpen
from sema.registry.property_format import SpaceheatName


class RcoRelayReading(SemaType):
    name: SpaceheatName
    value: RelayClosedOrOpen
    type_name: Literal["rco.relay.reading"] = "rco.relay.reading"
