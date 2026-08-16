from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_dac_channel_config import I2cDacChannelConfig


class SimDacWriterComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.dac.writer.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[I2cDacChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["sim.dac.writer.component.gt"] = "sim.dac.writer.component.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SimDacWriterComponentGt":
        """
        Axiom 1: DacChannelUniqueness
        DacChannel values SHALL be unique across the ConfigList.
        """
        dac_channels = [config.dac_channel for config in self.config_list]
        if len(dac_channels) != len(set(dac_channels)):
            raise ValueError(
                "Axiom 1 (DacChannelUniqueness) failed: DacChannel values must be "
                "unique across the ConfigList."
            )
        return self
