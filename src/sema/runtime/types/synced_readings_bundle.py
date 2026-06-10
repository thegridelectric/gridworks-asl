from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatTelemetryName
from sema.runtime.enums.old_versions.gw1_unit_001 import Gw1Unit001
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UtcIso8601Seconds
from sema.runtime.types.channel_readings_list_item import ChannelReadingsListItem


class SyncedReadingsBundle(SemaType):
    """Sema: https://schemas.electricity.works/types/synced.readings.bundle/002"""

    about_g_node_alias: LeftRightDot
    start_timestamp: UtcIso8601Seconds
    end_timestamp: UtcIso8601Seconds
    timestamp_list: list[UtcIso8601Seconds]
    channel_readings_list: list[ChannelReadingsListItem]
    type_name: Literal["synced.readings.bundle"] = "synced.readings.bundle"
    version: Literal["002"] = "002"

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
        Axiom 2: ChannelDefinitionBijection
        ChannelName values SHALL be unique across ChannelReadingsList.
        """
        seen = set()
        duplicates = set()
        for x in [crl.channel_name for crl in self.channel_readings_list]:
            if x in seen:
                duplicates.add(x)
            seen.add(x)

        if duplicates:
            raise ValueError(
                f"ChannelDefinitionBijection: ChannelName values {','.join(sorted(duplicates))} were repeated."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> Self:
        """
        Axiom 3: StartTimestampBeforeEnd
        StartTimestamp shall be less than EndTimestamp
        """
        if self.start_timestamp >= self.end_timestamp:
            raise ValueError(
                f"StartTimestampBeforeEnd: ({self.start_timestamp}) is not less than ({self.end_timestamp})."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> Self:
        """
        Axiom 4: TimestampAndValueLengthAlignment
        The length of TimestampList shall be equal to the length of ValueList for each entry in
        ChannelReadingsList.
        """
        errors = {}
        for crl in self.channel_readings_list:
            if len(crl.value_list) != len(self.timestamp_list):
                errors[crl.channel_name] = len(crl.value_list)

        if errors:
            err_detail = ", ".join(
                [f"len({key})={errors[key]}" for key in errors.keys()]
            )
            raise ValueError(
                f"TimestampAndValueLengthAlignment: len(timestamps)={len(self.timestamp_list)}, {err_detail}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_5(self) -> Self:
        """
        Axiom 5: UnitTypeAndValueRepresentationConsistency
        For each entry in ChannelDefinitions: - UnitType SHALL equal one of: gw1.unit
        spaceheat.telemetry.name - Unit SHALL be a valid value from the specified UnitType
        version: gw1.unit → version 001 spaceheat.telemetry.name → version 007
        """
        if Gw1Unit001.enum_version() != "001":
            raise ValueError(
                f'UnitTypeAndValueRepresentationConsistency: Gw1Unit version should be "001", is {Gw1Unit001.enum_version()}'
            )

        if SpaceheatTelemetryName.enum_version() != "007":
            raise ValueError(
                "UnitTypeAndValueRepresentationConsistency: "
                f'SpaceheatTelemetryName version should be "007", is {SpaceheatTelemetryName.enum_version()}'
            )

        errors = []
        for crl in self.channel_readings_list:
            if crl.unit_type == Gw1Unit001.enum_name():
                if crl.unit not in Gw1Unit001.values():
                    errors.append(
                        f"{crl.channel_name}: {crl.unit} not found in {crl.unit_type}"
                    )
            elif crl.unit_type == SpaceheatTelemetryName.enum_name():
                if crl.unit not in SpaceheatTelemetryName.values():
                    errors.append(
                        f"{crl.channel_name}: {crl.unit} not found in {crl.unit_type}"
                    )
            else:
                errors.append(f"{crl.channel_name}: invalid unit type {crl.unit_type}")

        if errors:
            raise ValueError(
                f"UnitTypeAndValueRepresentationConsistency: {', '.join(errors)}"
            )
        return self
