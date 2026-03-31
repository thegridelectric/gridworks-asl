from typing import Literal

from sema.registry.base import SemaType
from sema.registry.property_format import SpaceheatName, UTCMilliseconds


class SingleReading(SemaType):
    """Sema: https://schemas.electricity.works/types/single.reading/000"""

    channel_name: SpaceheatName
    value: int
    scada_read_time_unix_ms: UTCMilliseconds
    type_name: Literal["single.reading"] = "single.reading"
    version: Literal["000"] = "000"
