from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds


class GwChannelGapStats(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.channel.gap.stats/000"""

    channel_name: SpaceheatName
    channel_type_name: LeftRightDot
    channel_version: str
    window_start_unix_ms: UTCMilliseconds
    window_end_unix_ms: UTCMilliseconds
    num_readings: NonNegativeInt
    abs_gap_s: PositiveInt
    median_mult: PositiveFloat
    median_cadence_s: StrictFloat
    gap_count: NonNegativeInt
    excluded_gap_count: NonNegativeInt
    gapped_seconds: StrictFloat
    max_gap_dur_s: StrictFloat
    type_name: Literal["gw.channel.gap.stats"] = "gw.channel.gap.stats"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwChannelGapStats":
        """
        Axiom 1: WindowOrder
        WindowEndUnixMs SHALL be greater than WindowStartUnixMs.
        """
        if not self.window_end_unix_ms > self.window_start_unix_ms:
            raise ValueError(
                "Axiom 1 (WindowOrder) failed: WindowEndUnixMs must be greater "
                "than WindowStartUnixMs."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwChannelGapStats":
        """
        Axiom 2: NonNegativeDurations
        MedianCadenceS, GappedSeconds, and MaxGapDurS SHALL each be greater than
        or equal to zero.
        """
        if (
            self.median_cadence_s < 0
            or self.gapped_seconds < 0
            or self.max_gap_dur_s < 0
        ):
            raise ValueError(
                "Axiom 2 (NonNegativeDurations) failed: MedianCadenceS, "
                "GappedSeconds, and MaxGapDurS must each be >= 0."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwChannelGapStats":
        """
        Axiom 3: GapAccounting
        a. If GapCount is zero, GappedSeconds and MaxGapDurS SHALL be zero.
        b. If GapCount is greater than zero, GappedSeconds SHALL be greater
        than or equal to MaxGapDurS.
        """
        if self.gap_count == 0 and (
            self.gapped_seconds != 0 or self.max_gap_dur_s != 0
        ):
            raise ValueError(
                "Axiom 3 (GapAccounting) failed: with GapCount zero, "
                "GappedSeconds and MaxGapDurS must be zero."
            )
        if self.gap_count > 0 and self.gapped_seconds < self.max_gap_dur_s:
            raise ValueError(
                "Axiom 3 (GapAccounting) failed: GappedSeconds must be >= MaxGapDurS."
            )
        return self
