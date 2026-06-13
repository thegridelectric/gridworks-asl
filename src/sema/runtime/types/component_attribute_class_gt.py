from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.spaceheat_make_model_007 import (
    SpaceheatMakeModel007,
)
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str


class ComponentAttributeClassGt(SemaType):
    """Sema: https://schemas.electricity.works/types/component.attribute.class.gt/001"""

    component_attribute_class_id: UUID4Str
    make_model: SpaceheatMakeModel007
    display_name: str | None = None
    min_poll_period_ms: PositiveInt | None = None
    type_name: Literal["component.attribute.class.gt"] = "component.attribute.class.gt"
    version: Literal["001"] = "001"
