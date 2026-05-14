from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.ha1_params_004 import Ha1Params004
from sema.runtime.types.old_versions.ha1_params_005 import Ha1Params005
from sema.runtime.types.scada_params import ScadaParams


class ScadaParams004(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/004"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    new_params: Ha1Params004 | Ha1Params005 | None = None
    old_params: Ha1Params004 | Ha1Params005 | None = None
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["004"] = "004"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> ScadaParams:
        """
        - NewParams: ha1.params:004 | ha1.params:005 -> ha1.params:006
        - OldParams: ha1.params:004 | ha1.params:005 -> ha1.params:006
        """
        data = self.model_dump()
        if self.new_params is not None:
            new_params = self.new_params
            while new_params.version != "006":
                new_params = new_params.upgrade()
            data["new_params"] = new_params
        if self.old_params is not None:
            old_params = self.old_params
            while old_params.version != "006":
                old_params = old_params.upgrade()
            data["old_params"] = old_params
        data["version"] = "005"
        return ScadaParams.model_validate(data)
