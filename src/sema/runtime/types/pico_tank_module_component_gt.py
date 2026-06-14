from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_config import ChannelConfig


class PicoTankModuleComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.tank.module.component.gt/012"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[ChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    enabled: bool
    pico_hw_uid: str | None = None
    pico_a_hw_uid: str | None = None
    pico_b_hw_uid: str | None = None
    temp_calc_method: TempCalcMethod
    thermistor_beta: PositiveInt
    send_micro_volts: bool
    samples: PositiveInt
    num_sample_averages: PositiveInt
    pico_k_ohms: PositiveInt | None = None
    serial_number: str
    async_capture_delta_micro_volts: StrictInt
    sensor_order: list[StrictInt] | None = None
    type_name: Literal["pico.tank.module.component.gt"] = (
        "pico.tank.module.component.gt"
    )
    version: Literal["012"] = "012"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 1: PicoHardwareIdentityXor
        Exactly one of the following SHALL hold:
          - PicoHwUid is present
          - both PicoAHwUid and PicoBHwUid are present
        """
        raise NotImplementedError("Axiom 1 validation is not implemented.")

    @model_validator(mode="after")
    def check_axiom_2(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 2: PicoKOhmsConsistency
        PicoKOhms SHALL be present if and only if TempCalcMethod equals SimpleBetaForPico.
        """
        raise NotImplementedError("Axiom 2 validation is not implemented.")

    @model_validator(mode="after")
    def check_axiom_3(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 3: SensorOrderPermutation
        If SensorOrder is present, it SHALL be a permutation of [1, 2, 3].
        """
        raise NotImplementedError("Axiom 3 validation is not implemented.")
