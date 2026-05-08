from typing import Literal, Self
from pydantic import BaseModel, ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UtcIso8601Seconds


class ChannelReadingsListItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

    channel_name: SpaceheatName
    value_list: list[StrictInt]
    unit: str
    unit_type: LeftRightDot


class SyncedReadingsBundle(SemaType):
    """Sema: https://schemas.electricity.works/types/synced.readings.bundle/001"""

    about_g_node_alias: LeftRightDot
    start_timestamp: UtcIso8601Seconds
    end_timestamp: UtcIso8601Seconds
    timestamp_list: list[UtcIso8601Seconds]
    channel_readings_list: list[ChannelReadingsListItem]
    type_name: Literal["synced.readings.bundle"] = "synced.readings.bundle"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: TerminalAssetAliasConstraint
        AboutGNodeAlias SHALL identify a TerminalAsset and therefore SHALL end with the suffix
        ".ta".
        """
        if not self.about_g_node_alias.endswith(".ta"):
            raise ValueError(
                f'TerminalAssetAliasConstraint: AboutGNodeAlias ({self.about_g_node_alias}) does not end with the suffix ".ta".'
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: StartTimestampBeforeEnd
        StartTimestamp shall be less than EndTimestamp
        """
        if self.start_timestamp >= self.end_timestamp:
            raise ValueError(
                f"StartTimestampBeforeEnd: ({self.start_timestamp}) is not less than ({self.end_timestamp})."
            )
        return self
