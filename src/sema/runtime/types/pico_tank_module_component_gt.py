from typing import Literal

from pydantic import ConfigDict, StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.temp_calc_method import TempCalcMethod
from sema.runtime.property_format import PositiveInt, UUID4Str
from sema.runtime.types.channel_config import ChannelConfig


class PicoTankModuleComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/pico.tank.module.component.gt/011"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
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
    type_name: Literal["pico.tank.module.component.gt"] = "pico.tank.module.component.gt"
    version: Literal["011"] = "011"

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def check_axiom_1(self) -> "PicoTankModuleComponentGt":
        has_single = self.pico_hw_uid is not None
        has_pair = self.pico_a_hw_uid is not None and self.pico_b_hw_uid is not None
        if has_single == has_pair:
            raise ValueError(
                "Axiom 1 failed: exactly one of pico_hw_uid or both pico_a_hw_uid and pico_b_hw_uid must be present."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "PicoTankModuleComponentGt":
        if (self.temp_calc_method == TempCalcMethod.SimpleBetaForPico) != (
            self.pico_k_ohms is not None
        ):
            raise ValueError(
                "Axiom 2 failed: pico_k_ohms must be present iff temp_calc_method is SimpleBetaForPico."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "PicoTankModuleComponentGt":
        if self.sensor_order is not None and sorted(self.sensor_order) != [1, 2, 3]:
            raise ValueError(
                "Axiom 3 failed: sensor_order must be a permutation of [1, 2, 3]."
            )
        return self
