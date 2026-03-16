from typing import Literal

from sema.registry.base import SemaType
from sema.registry.enums import (
    GNodeInstanceTransport,
    FisAuthorizationDecision,
    FisAuthorizationReason,
)
from sema.registry.property_format import (
    UUID4Str,
    LeftRightDot,
    UTCMilliseconds,
)


class FisInstanceAuthorizationEvent(SemaType):
    """
    Sema:
    https://schemas.electricity.works/types/fis.instance.authorization.event/000
    """

    event_id: UUID4Str
    g_node_id: UUID4Str
    g_node_instance_id: UUID4Str

    decision: FisAuthorizationDecision
    reason: FisAuthorizationReason
    transport: GNodeInstanceTransport

    decided_at_unix_ms: UTCMilliseconds

    g_node_alias: LeftRightDot | None = None
    observed_peer_address: str | None = None
    connection_handle: str | None = None

    type_name: Literal[
        "fis.instance.authorization.event"
    ] = "fis.instance.authorization.event"

    version: Literal["000"] = "000"