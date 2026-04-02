from typing import Literal

from sema.runtime import SemaType
from sema.runtime.enums import RelayClosedOrOpen
from sema.runtime.property_format import SpaceheatName


class RcoRelayReading(SemaType):
    name: SpaceheatName
    value: RelayClosedOrOpen
    type_name: Literal["rco.relay.reading"] = "rco.relay.reading"
