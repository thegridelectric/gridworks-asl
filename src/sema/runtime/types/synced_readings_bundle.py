<<<<<<< HEAD
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
=======
from typing import List, Literal, Self
from pydantic import BaseModel, ConfigDict, StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_unit import Gw1Unit
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.runtime.property_format import LeftRightDot, SpaceheatName, UtcIso8601Seconds

class ChannelReadingsListItem(BaseModel):
    channel_name: SpaceheatName
    value_list: List[StrictInt | None]
>>>>>>> 381ee30be2f1a9970c87415d22c8e0a7a23c1a73
    unit: str
    unit_type: LeftRightDot

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

<<<<<<< HEAD

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
=======
class SyncedReadingsBundleGt(SemaType):
    about_gnode_alias: LeftRightDot
    start_timestamp: UtcIso8601Seconds
    end_timestamp: UtcIso8601Seconds
    timestamp_list: List[UtcIso8601Seconds]
    channel_readings_list: List[ChannelReadingsListItem]
    type_name: Literal["synced.readings.bundle"] = "synced.readings.bundle"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom1(self) -> Self:
        """
        Axiom 1: "AboutGNodeAlias SHALL identify a TerminalAsset and therefore SHALL end with the suffix ".ta"."
        """
        if not self.about_gnode_alias.endswith(".ta"):
            raise ValueError(
                f'TerminalAssetAliasConstraint: AboutGNodeAlias ({self.about_gnode_alias}) does not end with the suffix ".ta".'
            )

        return self

    @model_validator(mode="after")
    def check_axiom2(self) -> Self:
        """
        Axiom 2: "ChannelName values SHALL be unique across ChannelReadingsList."
        """

        seen = set()
        duplicates = set()
        for x in [crl.channel_name for crl in self.channel_readings_list]:
            if x in seen:
                duplicates.add(x)
            seen.add(x)

        if len(duplicates) > 0:
            raise ValueError(
                f'ChannelDefinitionBijection: ChannelName values {str.join(",", duplicates)} were repeated.'
            )

        return self

    @model_validator(mode="after")
    def check_axiom3(self) -> Self:
        """
        Axiom 3: "StartTimestamp shall be less than EndTimestamp"
        """

        if self.start_timestamp >= self.end_timestamp:
            raise ValueError(
                f'StartTimestampBeforeEnd: ({self.start_timestamp}) is not less than {(self.end_timestamp)}.'
            )

        return self

    @model_validator(mode="after")
    def check_axiom4(self) -> Self:
        """
        Axiom 4: "The length of TimestampList shall be equal to the length of ValueList for each entry in ChannelReadingsList."
        """
        errors = {}
        for crl in self.channel_readings_list:
            if len(crl.value_list) != len(self.timestamp_list):
                errors[crl.channel_name] = len(crl.value_list)

        if len(errors.keys()) > 0:
            err_detail = str.join(', ', [f'len({key})={errors[key]}' for key in errors.keys()])
            raise ValueError(
                f'TimestampAndValueLengthAlignment: len(timestamps)={len(crl.value_list)}, {err_detail}.'
            )

        return self

    @model_validator(mode="after")
    def check_axiom5(self) -> Self:
        """
        Axiom 5: "For each entry in ChannelDefinitions:

          - UnitType SHALL equal one of:
              gw1.unit
              spaceheat.telemetry.name

          - Unit SHALL be a valid value from the specified UnitType version:

            gw1.unit → version 001
            spaceheat.telemetry.name → version 007"

        """

        if Gw1Unit.enum_version() != "001":
            raise ValueError(f'UnitTypeAndValueRepresentationConsistency: Gw1Unit version should be "001", is "{Gw1Unit.enum_version()}"')

        if SpaceheatTelemetryName.enum_version() != "007":
            raise ValueError(f'UnitTypeAndValueRepresentationConsistency: SpaceheatTelemetryName version should be "007", is "{SpaceheatTelemetryName.enum_version()}"')

        errors = []
        for crl in self.channel_readings_list:
            if crl.unit_type == Gw1Unit.enum_name():
                if crl.unit not in Gw1Unit.values():
                    errors.append(f'{crl.channel_name}: {crl.unit} not found in {crl.unit_type}')
            elif crl.unit_type == SpaceheatTelemetryName.enum_name():
                if crl.unit not in SpaceheatTelemetryName.values():
                    errors.append(f'{crl.channel_name}: {crl.unit} not found in {crl.unit_type}')
            else:
                errors.append(f'{crl.channel_name}: invalid unit type {crl.unit_type}')

        if len(errors) > 0:
            raise ValueError(f'UnitTypeAndValueRepresentationConsistency: {str.join(', ', errors)}')

>>>>>>> 381ee30be2f1a9970c87415d22c8e0a7a23c1a73
        return self
