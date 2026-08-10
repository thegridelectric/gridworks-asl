from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_dac_channel_config import I2cDacChannelConfig


class I2cDacWriterComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.dac.writer.component.gt/000"""

    component_id: UUID4Str
    board_component_id: UUID4Str
    dac_name: PascalCase
    config_list: list[I2cDacChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["i2c.dac.writer.component.gt"] = "i2c.dac.writer.component.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cDacWriterComponentGt":
        """
        Axiom 1: DacChannelUniqueness
        DacChannel values SHALL be unique across the ConfigList.
        """
        channels = [cfg.dac_channel for cfg in self.config_list]
        dupes = sorted({str(c) for c in channels if channels.count(c) > 1})
        if dupes:
            raise ValueError(
                "Axiom 1 (DacChannelUniqueness) failed: duplicate DacChannel "
                f"value(s) {dupes} in ConfigList."
            )
        return self
