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
        Axiom 1: ChannelNameUniqueness
        Channel names SHALL be unique across the ConfigList.
        """
        channel_names = [config.channel_name for config in self.config_list]
        if len(channel_names) != len(set(channel_names)):
            raise ValueError(
                "Axiom 1 (ChannelNameUniqueness) failed: channel names must be "
                "unique across the ConfigList."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 2: PicoHardwareIdentityXor
        Exactly one of the following SHALL hold:
          - PicoHwUid is present
          - both PicoAHwUid and PicoBHwUid are present
        """
        single = self.pico_hw_uid is not None
        pair = self.pico_a_hw_uid is not None and self.pico_b_hw_uid is not None
        if single == pair:
            raise ValueError(
                "Axiom 2 (PicoHardwareIdentityXor): exactly one of PicoHwUid, "
                "or both PicoAHwUid and PicoBHwUid, SHALL be present."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 3: PicoKOhmsConsistency
        PicoKOhms SHALL be present if and only if TempCalcMethod equals SimpleBetaForPico.
        """
        kohms_present = self.pico_k_ohms is not None
        is_pico_beta = (
            str(getattr(self.temp_calc_method, "value", self.temp_calc_method))
            == "SimpleBetaForPico"
        )
        if kohms_present != is_pico_beta:
            raise ValueError(
                "Axiom 3 (PicoKOhmsConsistency): PicoKOhms SHALL be present "
                "if and only if TempCalcMethod is SimpleBetaForPico."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "PicoTankModuleComponentGt":
        """
        Axiom 4: SensorOrderPermutation
        If SensorOrder is present, it SHALL be a permutation of [1, 2, 3].
        """
        if self.sensor_order is not None and sorted(self.sensor_order) != [1, 2, 3]:
            raise ValueError(
                "Axiom 4 (SensorOrderPermutation): SensorOrder SHALL be a "
                "permutation of [1, 2, 3]."
            )
        return self
