from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatTelemetryName
from sema.runtime.enums.old_versions.spaceheat_make_model_007 import (
    SpaceheatMakeModel007,
)
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str


class ElectricMeterCacGt(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.cac.gt/001"""

    component_attribute_class_id: UUID4Str
    make_model: SpaceheatMakeModel007
    display_name: str | None = None
    min_poll_period_ms: PositiveInt | None = None
    telemetry_name_list: list[SpaceheatTelemetryName]
    default_baud: StrictInt | None = None
    type_name: Literal["electric.meter.cac.gt"] = "electric.meter.cac.gt"
    version: Literal["001"] = "001"
