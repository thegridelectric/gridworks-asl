from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cAdcChannel
from sema.runtime.enums import I2cAdcType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GwAdcWaveform(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.adc.waveform/000"""

    ta_alias: LeftRightDot
    message_id: UUID4Str
    message_created_ms: UTCMilliseconds
    adc_type: I2cAdcType
    i2c_address: PositiveInt
    adc_channel: I2cAdcChannel
    full_scale_millivolts: PositiveInt
    data_rate_hz: PositiveInt
    start_unix_ms: UTCMilliseconds
    sample_offsets_us: list[StrictInt]
    codes: list[StrictInt]
    type_name: Literal["gw.adc.waveform"] = "gw.adc.waveform"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwAdcWaveform":
        """
        Axiom 1: PairedNonEmptyLists
        a. Codes SHALL be non-empty. b. len(SampleOffsetsUs) SHALL equal len(Codes).
        """
        if len(self.codes) == 0:
            raise ValueError(
                "Axiom 1 (PairedNonEmptyLists) failed: Codes must be non-empty."
            )
        if len(self.sample_offsets_us) != len(self.codes):
            raise ValueError(
                "Axiom 1 (PairedNonEmptyLists) failed: len(SampleOffsetsUs) "
                f"{len(self.sample_offsets_us)} must equal len(Codes) {len(self.codes)}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwAdcWaveform":
        """
        Axiom 2: OffsetsAnchoredIncreasing
        a. The first element of SampleOffsetsUs SHALL be 0. b. SampleOffsetsUs SHALL be
        strictly increasing.
        """
        offsets = self.sample_offsets_us
        if offsets and offsets[0] != 0:
            raise ValueError(
                "Axiom 2 (OffsetsAnchoredIncreasing) failed: the first "
                f"SampleOffsetsUs element must be 0, got {offsets[0]}."
            )
        for i in range(1, len(offsets)):
            if offsets[i] <= offsets[i - 1]:
                raise ValueError(
                    "Axiom 2 (OffsetsAnchoredIncreasing) failed: SampleOffsetsUs "
                    f"must be strictly increasing; index {i} ({offsets[i]}) is not "
                    f"greater than index {i - 1} ({offsets[i - 1]})."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwAdcWaveform":
        """
        Axiom 3: SixteenBitCodes
        Every element of Codes SHALL be between -32768 and 32767 inclusive.
        """
        for i, code in enumerate(self.codes):
            if code < -32768 or code > 32767:
                raise ValueError(
                    "Axiom 3 (SixteenBitCodes) failed: Codes must be within "
                    f"[-32768, 32767]; index {i} is {code}."
                )
        return self
