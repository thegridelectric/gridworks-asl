from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.i2c_operation_000 import I2cOperation000
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_result import I2cResult


class I2cResult000(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.result/000"""

    bus: SpaceheatName
    operation: I2cOperation000
    value: NonNegativeInt | None = None
    success: bool
    error: str | None = None
    unix_time_ms: UTCMilliseconds
    trigger_id: UUID4Str
    type_name: Literal["i2c.result"] = "i2c.result"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cResult000":
        """
        Axiom 1: ErrorIffFailure
        Error SHALL be present and non-blank if and only if Success is false.
        """
        has_error = self.error is not None and self.error.strip() != ""
        if self.success and has_error:
            raise ValueError(
                "Axiom 1 (ErrorIffFailure) failed: Success is true but Error is present."
            )
        if not self.success and not has_error:
            raise ValueError(
                "Axiom 1 (ErrorIffFailure) failed: Success is false but Error is missing or blank."
            )
        return self

    def upgrade(self) -> I2cResult:
        """Operation ref moves to i2c.operation/001; optional Bytes list for
        multi-byte (ReadBytes) results."""
        data = self.model_dump()
        data["version"] = "001"
        return I2cResult.model_validate(data)
