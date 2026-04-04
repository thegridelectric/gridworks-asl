from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1Unit, SpaceheatTelemetryName
from sema.runtime.property_format import (
    LeftRightDot,
    SpaceheatName,
    UUID4Str,
    UtcIso8601Seconds,
)


class ChannelReadingsList(BaseModel):
    channel_name: SpaceheatName
    value_list: list[StrictInt]

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )


class ChannelDefinition(BaseModel):
    name: SpaceheatName
    id: UUID4Str
    unit: str
    unit_type: LeftRightDot

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )


class SyncedReadingsBundle(SemaType):
    """Sema: https://schemas.electricity.works/types/synced.readings.bundle/000"""

    about_g_node_alias: LeftRightDot
    start: UtcIso8601Seconds
    end: UtcIso8601Seconds
    timestamp_list: list[UtcIso8601Seconds]
    channel_readings_list: list[ChannelReadingsList]
    channel_definitions: list[ChannelDefinition]
    type_name: Literal["synced.readings.bundle"] = "synced.readings.bundle"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SyncedReadingsBundle":
        if not self.about_g_node_alias.endswith(".ta"):
            raise ValueError(
                "Axiom 1 failed: about_g_node_alias must identify a TerminalAsset and end with '.ta'."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "SyncedReadingsBundle":
        channel_names = [entry.channel_name for entry in self.channel_readings_list]
        definition_names = [entry.name for entry in self.channel_definitions]
        definition_ids = [entry.id for entry in self.channel_definitions]

        if len(channel_names) != len(set(channel_names)):
            raise ValueError(
                "Axiom 2 failed: channel_name values must be unique across channel_readings_list."
            )
        if len(definition_names) != len(set(definition_names)):
            raise ValueError(
                "Axiom 2 failed: name values must be unique across channel_definitions."
            )
        if len(definition_ids) != len(set(definition_ids)):
            raise ValueError(
                "Axiom 2 failed: id values must be unique across channel_definitions."
            )
        if set(channel_names) != set(definition_names):
            raise ValueError(
                "Axiom 2 failed: channel_readings_list channel names must match channel_definitions names."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "SyncedReadingsBundle":
        expected_length = len(self.timestamp_list)
        for entry in self.channel_readings_list:
            if len(entry.value_list) != expected_length:
                raise ValueError(
                    "Axiom 3 failed: each value_list must have the same length as timestamp_list."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "SyncedReadingsBundle":
        for entry in self.channel_definitions:
            if entry.unit_type == "gw1.unit":
                Gw1Unit(entry.unit)
            elif entry.unit_type == "spaceheat.telemetry.name":
                SpaceheatTelemetryName(entry.unit)
            else:
                raise ValueError(
                    "Axiom 4 failed: unit_type must be gw1.unit or spaceheat.telemetry.name."
                )
        return self
