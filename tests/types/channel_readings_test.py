from pydantic import ValidationError

from sema.runtime.types.channel_readings import ChannelReadings


def test_channel_readings_length_validator() -> None:
    try:
        ChannelReadings(
            channel_name="hp-odu-pwr",
            value_list=[1, 2],
            scada_read_time_unix_ms_list=[1735689600123],
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
