from pydantic import ValidationError

from sema.runtime.types.channel_config import ChannelConfig


def test_channel_config_serializes_pascal_case() -> None:
    cfg = ChannelConfig(
        channel_name="zone1-relay-state",
        capture_period_s=60,
        async_capture=True,
        async_capture_delta=1,
        exponent=0,
        unit="Unitless",
    )
    dumped = cfg.to_dict()
    assert dumped["ChannelName"] == "zone1-relay-state"
    assert dumped["TypeName"] == "channel.config"
    assert dumped["Version"] == "000"


def test_channel_config_async_capture_requires_delta() -> None:
    cfg = ChannelConfig(
        channel_name="zone1-relay-state",
        capture_period_s=60,
        async_capture=True,
        exponent=0,
        unit="Unitless",
    )
    assert cfg.async_capture_delta is None


def test_channel_config_rejects_float_for_integer_field() -> None:
    try:
        ChannelConfig(
            channel_name="zone1-relay-state",
            capture_period_s=60.0,
            async_capture=True,
            exponent=0,
            unit="Unitless",
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
