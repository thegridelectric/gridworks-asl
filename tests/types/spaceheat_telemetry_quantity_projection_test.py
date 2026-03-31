from pydantic import ValidationError

from sema.registry.types.spaceheat_telemetry_quantity_projection import (
    SpaceheatTelemetryQuantityProjection,
)


def test_projection_mapping_validator() -> None:
    try:
        SpaceheatTelemetryQuantityProjection(
            telemetry_name="PowerW",
            quantity="Temperature",
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
