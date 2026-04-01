from pydantic import ValidationError

from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.relay_actor_config import RelayActorConfig


def test_i2c_multichannel_dt_relay_component_gt_uniqueness() -> None:
    cfg = RelayActorConfig(
        channel_name="zone1-relay",
        poll_period_ms=200,
        capture_period_s=60,
        async_capture=True,
        async_capture_delta=1,
        exponent=0,
        unit="Unitless",
        relay_idx=1,
        actor_name="relay1",
        wiring_config="NormallyClosed",
        event_type="change.relay.state",
        de_energizing_event="CloseRelay",
        energizing_event="OpenRelay",
        state_type="relay.closed.or.open",
        de_energized_state="RelayClosed",
        energized_state="RelayOpen",
    )
    try:
        I2cMultichannelDtRelayComponentGt(
            component_id=str(__import__("uuid").uuid4()),
            component_attribute_class_id=str(__import__("uuid").uuid4()),
            config_list=[cfg, cfg],
            i2c_address_list=[32, 33],
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
