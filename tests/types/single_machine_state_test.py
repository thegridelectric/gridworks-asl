from pydantic import ValidationError

from sema.registry.types.single_machine_state import SingleMachineState


def test_single_machine_state_known_enum_validation() -> None:
    try:
        SingleMachineState(
            machine_handle="auto.local-control.local-control-normal.relay6",
            state_enum="relay.closed.or.open",
            state="BadState",
            unix_ms=1764873285123,
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
