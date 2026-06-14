from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, StrictInt
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_config import ChannelConfig
from sema.runtime.types.web_server_component_gt import WebServerComponentGt


class WebServer(BaseModel):
    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

    enabled: bool
    host: str
    name: str
    port: StrictInt
    kwargs: dict[str, Any]


class WebServerComponentGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/web.server.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ChannelConfig]
    web_server: WebServer
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["web.server.component.gt"] = "web.server.component.gt"
    version: Literal["001"] = "001"

    def upgrade(self) -> WebServerComponentGt:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "WebServerComponentGt001 cannot be upgraded to "
            "WebServerComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
