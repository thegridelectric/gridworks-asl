from typing import Literal
from pydantic import StrictFloat
from sema.runtime.base import SemaType
from sema.runtime.types.linear_one_dimensional_calibration import LinearOneDimensionalCalibration


class LinearOneDimensionalCalibration000(SemaType):
    """Sema: https://schemas.electricity.works/types/linear.one.dimensional.calibration/000"""

    m: StrictFloat = 1.0
    b: StrictFloat = 0.0
    type_name: Literal["linear.one.dimensional.calibration"] = "linear.one.dimensional.calibration"
    version: Literal["000"] = "000"

    def upgrade(self) -> LinearOneDimensionalCalibration:
        """
        - B: number -> integer
        - Semantics: clarify OutputUnit scaling domain
        """
        raise ValueError(
            "LinearOneDimensionalCalibration000 cannot be "
            "upgraded to LinearOneDimensionalCalibration "
            "without calibration source context needed to convert B into the "
            "OutputUnit scaling domain."
        )
