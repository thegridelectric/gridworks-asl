from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GNodeInstanceStatus
from sema.runtime.enums import GNodeInstanceTransport
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GNodeInstanceGt(SemaType):
    """Sema: https://schemas.electricity.works/types/g.node.instance.gt/000"""

    g_node_id: UUID4Str
    g_node_instance_id: UUID4Str
    status: GNodeInstanceStatus
    transport: GNodeInstanceTransport
    connected_at_unix_ms: UTCMilliseconds
    revoked_at_unix_ms: UTCMilliseconds | None = None
    connection_handle: str | None = None
    observed_peer_address: str | None = None
    type_name: Literal["g.node.instance.gt"] = "g.node.instance.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: RevocationTimestampConsistency
        RevokedAtUnixMs SHALL be present if and only if Status is Revoked or Ended.
        """

        if self.status in {
            GNodeInstanceStatus.Revoked,
            GNodeInstanceStatus.Ended,
        }:
            if self.revoked_at_unix_ms is None:
                raise ValueError(
                    "Axiom 1 violated! RevokedAtUnixMs must be present "
                    "when Status is Revoked or Ended."
                )

        if self.status == GNodeInstanceStatus.Active:
            if self.revoked_at_unix_ms is not None:
                raise ValueError(
                    "Axiom 1 violated! RevokedAtUnixMs must be null "
                    "when Status is Active."
                )

        return self
