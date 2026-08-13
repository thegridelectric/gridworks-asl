from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1ActuationAuthority
from sema.runtime.enums import Gw1ServiceMode
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.types.capture_tuning import CaptureTuning
from sema.runtime.types.cop_curve import CopCurve
from sema.runtime.types.gw_tou_window import GwTouWindow
from sema.runtime.types.heating_curve import HeatingCurve


class GwNolanOperationalParams(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.nolan.operational.params/000"""

    scada_alias: LeftRightDot
    capture_tuning_list: list[CaptureTuning]
    actuation_authority: Gw1ActuationAuthority
    service_mode: Gw1ServiceMode
    cop_curve: CopCurve
    heating_curve: HeatingCurve
    on_peak_windows: list[GwTouWindow]
    held_circuit_positions: list[PositiveInt]
    type_name: Literal["gw.nolan.operational.params"] = "gw.nolan.operational.params"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwNolanOperationalParams":
        """
        Axiom 1: CaptureTuningChannelUniqueness
        ChannelName SHALL be unique across CaptureTuningList.
        """
        names = [ct.channel_name for ct in self.capture_tuning_list]
        if len(names) != len(set(names)):
            raise ValueError(
                "Axiom 1 (CaptureTuningChannelUniqueness) failed: ChannelName "
                "must be unique across CaptureTuningList."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwNolanOperationalParams":
        """
        Axiom 2: PerDayWindowNonOverlap
        For each day of the week, the windows in OnPeakWindows whose Days include that day
        SHALL NOT overlap one another.
        """
        days = {day for w in self.on_peak_windows for day in w.days}
        for day in days:
            todays = sorted(
                (w for w in self.on_peak_windows if day in w.days),
                key=lambda w: w.start,
            )
            for earlier, later in zip(todays, todays[1:]):
                if later.start < earlier.end:
                    raise ValueError(
                        "Axiom 2 (PerDayWindowNonOverlap) failed: on "
                        f"{day} window {later.start}-{later.end} overlaps "
                        f"{earlier.start}-{earlier.end}."
                    )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwNolanOperationalParams":
        """
        Axiom 3: HeldCircuitPositionUniqueness
        HeldCircuitPositions SHALL NOT contain duplicate values.
        """
        if len(self.held_circuit_positions) != len(set(self.held_circuit_positions)):
            raise ValueError(
                "Axiom 3 (HeldCircuitPositionUniqueness) failed: "
                "HeldCircuitPositions must not contain duplicate values."
            )
        return self
