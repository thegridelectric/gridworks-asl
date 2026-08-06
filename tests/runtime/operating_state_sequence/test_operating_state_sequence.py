from pydantic import ValidationError

from sema.runtime.types.operating_state_sequence import OperatingStateSequence

# The valid object is the beech 2026-02-10 local-control sequence from the
# schema's extended_description example.

def test_valid_object() -> None:
    OperatingStateSequence(
        channel_name="local-control-all-tanks-state",
        value_list=[
            "HpOffStoreOff",
            "HpOffStoreDischarge",
        ],
        timestamp_list=[
            "2026-02-10T11:58:42.099Z",
            "2026-02-10T11:59:42.105Z",
        ],
    )

def test_axiom1_length_consistency() -> None:
    try:
        OperatingStateSequence(
            channel_name="pico-cycler-state",
            value_list=["RelayOpening", "RelayOpen"],
            timestamp_list=["2026-02-10T17:15:00.221Z"],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "Axiom 1" not in repr(e):
            raise AssertionError("Expected Axiom 1 error, found something else", e)

def test_axiom2_strictly_increasing() -> None:
    try:
        OperatingStateSequence(
            channel_name="pico-cycler-state",
            value_list=["RelayOpening", "RelayOpen"],
            timestamp_list=["2026-02-10T17:15:00.221Z", "2026-02-10T17:15:00.221Z"],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError as e:
        if "Axiom 2" not in repr(e):
            raise AssertionError("Expected Axiom 2 error, found something else", e)

def test_value_must_be_pascal_case() -> None:
    try:
        OperatingStateSequence(
            channel_name="pico-cycler-state",
            value_list=["relay-opening"],
            timestamp_list=["2026-02-10T17:15:00.221Z"],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError:
        pass

def test_timestamp_must_have_millis() -> None:
    try:
        OperatingStateSequence(
            channel_name="pico-cycler-state",
            value_list=["RelayOpening"],
            timestamp_list=["2026-02-10T17:15:00Z"],
        )
        raise AssertionError("Expected validation failure")
    except ValidationError:
        pass
