import sys
from pydantic import ValidationError

from sema.runtime.types.synced_readings_bundle import (
    ChannelReadingsListItem,
    SyncedReadingsBundle,
)


def test_valid_object() -> None:
    SyncedReadingsBundle(
        about_g_node_alias="a.b.c.ta",
        start_timestamp="2025-02-26T00:00:00Z",
        end_timestamp="2025-02-26T02:00:00Z",
        timestamp_list=[
            "2025-02-26T00:00:00Z",
            "2025-02-26T00:01:00Z",
            "2025-02-26T00:02:00Z",
        ],
        channel_readings_list=[
            ChannelReadingsListItem(
                channel_name="buffer-depth1",
                value_list=[4973, 4966, 4979],
                unit="FahrenheitX100",
                unit_type="gw1.unit",
            ),
            ChannelReadingsListItem(
                channel_name="hp-ewt",
                value_list=[18234, 18179, 18157],
                unit="WaterTempCTimes1000",
                unit_type="spaceheat.telemetry.name",
            ),
            ChannelReadingsListItem(
                channel_name="hp-idu-pwr",
                value_list=[14, 14, 14],
                unit="FahrenheitX100",
                unit_type="gw1.unit",
            ),
            ChannelReadingsListItem(
                channel_name="persistence-delay",
                value_list=[231, 102, 3650238],
                unit="Milliseconds",
                unit_type="gw1.unit",
            ),
        ],
        late_persistence_time_period_list=[],
        operating_state_sequence_list=[],
    )

def test_axiom1() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c",
            start_timestamp="2025-02-26T00:00:00Z",
            end_timestamp="2025-02-26T02:00:00Z",
            timestamp_list=[],
            channel_readings_list=[],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "TerminalAssetAliasConstraint" not in repr(e):
            raise AssertionError("Expected TerminalAssetAliasConstraint error, found something else", e)

def test_axiom2() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c.ta",
            start_timestamp="2025-02-26T00:00:00Z",
            end_timestamp="2025-02-26T02:00:00Z",
            timestamp_list=["2025-02-26T00:00:00Z"],
            channel_readings_list=[
                ChannelReadingsListItem(
                    channel_name="persistence-delay",
                    value_list=[1],
                    unit="Milliseconds",
                    unit_type="gw1.unit",
                ),
                ChannelReadingsListItem(
                    channel_name="persistence-delay",
                    value_list=[2],
                    unit="Milliseconds",
                    unit_type="gw1.unit",
                ),
            ],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "ChannelDefinitionBijection" not in repr(e):
            raise AssertionError("Expected ChannelDefinitionBijection error, found something else", e)

def test_axiom3() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c.ta",
            start_timestamp="2025-02-26T02:00:00Z",
            end_timestamp="2025-02-26T00:00:00Z",
            timestamp_list=[],
            channel_readings_list=[],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "StartTimestampBeforeEnd" not in repr(e):
            raise AssertionError("Expected StartTimestampBeforeEnd error, found something else", e)

def test_axiom4() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c.ta",
            start_timestamp="2025-02-26T00:00:00Z",
            end_timestamp="2025-02-26T02:00:00Z",
            timestamp_list=["2025-02-26T00:00:00Z", "2025-02-26T01:00:00Z"],
            channel_readings_list=[
                ChannelReadingsListItem(
                    channel_name="persistence-delay",
                    value_list=[1,20],
                    unit="Milliseconds",
                    unit_type="gw1.unit",
                ),
                ChannelReadingsListItem(
                    channel_name="persistence-delay2",
                    value_list=[2],
                    unit="Milliseconds",
                    unit_type="gw1.unit",
                ),
            ],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "TimestampAndValueLengthAlignment" not in repr(e):
            raise AssertionError("Expected TimestampAndValueLengthAlignment error, found something else", e)

def test_axiom5_invalid_unit_type() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c.ta",
            start_timestamp="2025-02-26T00:00:00Z",
            end_timestamp="2025-02-26T02:00:00Z",
            timestamp_list=["2025-02-26T00:00:00Z", "2025-02-26T01:00:00Z"],
            channel_readings_list=[
                ChannelReadingsListItem(
                    channel_name="persistence-delay",
                    value_list=[1,20],
                    unit="Milliseconds",
                    unit_type="something.else",
                ),
            ],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "UnitTypeAndValueRepresentationConsistency" not in repr(e):
            raise AssertionError("Expected UnitTypeAndValueRepresentationConsistency error, found something else", e)

def test_axiom5_invalid_unit() -> None:
    try:
        SyncedReadingsBundle(
            about_g_node_alias="a.b.c.ta",
            start_timestamp="2025-02-26T00:00:00Z",
            end_timestamp="2025-02-26T02:00:00Z",
            timestamp_list=["2025-02-26T00:00:00Z", "2025-02-26T01:00:00Z"],
            channel_readings_list=[
                ChannelReadingsListItem(
                    channel_name="persistence-delay",
                    value_list=[1,20],
                    unit="SomethingElse",
                    unit_type="gw1.unit",
                ),
            ],
            late_persistence_time_period_list=[],
            operating_state_sequence_list=[],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "UnitTypeAndValueRepresentationConsistency" not in repr(e):
            raise AssertionError("Expected UnitTypeAndValueRepresentationConsistency error, found something else", e)
