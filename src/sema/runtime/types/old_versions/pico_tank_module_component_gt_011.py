from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import TempCalcMethod
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.channel_config_000 import ChannelConfig000
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt


class PicoTankModuleComponentGt011(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.tank.module.component.gt/011"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[ChannelConfig000]
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
    version: Literal["011"] = "011"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "PicoTankModuleComponentGt011":
        """
        Axiom 1: PicoHardwareIdentityXor
        Exactly one of the following SHALL hold: - PicoHwUid is present - both PicoAHwUid and
        PicoBHwUid are present
        """
        has_single = self.pico_hw_uid is not None
        has_pair = self.pico_a_hw_uid is not None and self.pico_b_hw_uid is not None
        if has_single == has_pair:
            raise ValueError(
                "Axiom 1 failed: exactly one of pico_hw_uid or both pico_a_hw_uid and pico_b_hw_uid must be present."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "PicoTankModuleComponentGt011":
        """
        Axiom 2: PicoKOhmsConsistency
        PicoKOhms SHALL be present if and only if TempCalcMethod equals SimpleBetaForPico.
        """
        if (self.temp_calc_method == TempCalcMethod.SimpleBetaForPico) != (
            self.pico_k_ohms is not None
        ):
            raise ValueError(
                "Axiom 2 failed: pico_k_ohms must be present iff temp_calc_method is SimpleBetaForPico."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "PicoTankModuleComponentGt011":
        """
        Axiom 3: SensorOrderPermutation
        If SensorOrder is present, it SHALL be a permutation of [1, 2, 3].
        """
        if self.sensor_order is not None and sorted(self.sensor_order) != [1, 2, 3]:
            raise ValueError(
                "Axiom 3 failed: sensor_order must be a permutation of [1, 2, 3]."
            )
        return self

    def upgrade(self) -> PicoTankModuleComponentGt:
        """
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case). Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "PicoTankModuleComponentGt011 cannot be upgraded to "
            "PicoTankModuleComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
