from typing import List, Literal

from pydantic import BaseModel, field_validator, ConfigDict

from sema.registry import SemaType
from sema.registry.property_format import (
    LeftRightDot,
    SpaceheatName,
    UtcIso8601Seconds,
)


class ChannelReadings(BaseModel):
    channel_name: SpaceheatName
    value_list: List[int]

    model_config = ConfigDict(extra="forbid")


class ChannelDefinition(BaseModel):
    name: SpaceheatName
    unit: str

    model_config = ConfigDict(extra="forbid")


class SyncedReadingsBundle(SemaType):
    about_gnode_alias: LeftRightDot

    start: UtcIso8601Seconds
    end: UtcIso8601Seconds

    timestamp_list: List[UtcIso8601Seconds]

    channel_readings_list: List[ChannelReadings]
    channel_definitions: List[ChannelDefinition]

    type_name: Literal["synced.readings.bundle"] = "synced.readings.bundle"
    version: Literal["000"] = "000"

    model_config = ConfigDict(extra="forbid")

    # -------------------------
    # Axiom 1: TerminalAssetAliasConstraint
    # -------------------------
    @field_validator("about_gnode_alias")
    @classmethod
    def check_terminal_asset(cls, v: str) -> str:
        if not v.endswith(".ta"):
            raise ValueError(f"{v}: must end with '.ta'")
        return v

    # -------------------------
    # Axiom 3: TimestampAlignment
    # -------------------------
    @field_validator("channel_readings_list")
    @classmethod
    def check_timestamp_alignment(cls, readings, info):
        timestamps = info.data.get("timestamp_list")
        if timestamps is None:
            return readings

        n = len(timestamps)

        for r in readings:
            if len(r.value_list) != n:
                raise ValueError(
                    f"{r.channel_name}: ValueList length {len(r.value_list)} != {n}"
                )

        return readings

    # -------------------------
    # Axiom 2: ChannelDefinitionBijection
    # -------------------------
    @field_validator("channel_definitions")
    @classmethod
    def check_bijection(cls, defs, info):
        readings = info.data.get("channel_readings_list")
        if readings is None:
            return defs

        r_names = [r.channel_name for r in readings]
        d_names = [d.name for d in defs]

        if len(set(r_names)) != len(r_names):
            raise ValueError("Duplicate channel_name in channel_readings_list")

        if len(set(d_names)) != len(d_names):
            raise ValueError("Duplicate name in channel_definitions")

        if set(r_names) != set(d_names):
            raise ValueError(
                "ChannelReadingsList and ChannelDefinitions must have identical name sets"
            )

        return defs