from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.ha1_params_001 import Ha1Params001
from sema.runtime.types.old_versions.ha1_params_002 import Ha1Params002
from sema.runtime.types.old_versions.ha1_params_003 import Ha1Params003
from sema.runtime.types.old_versions.scada_params_004 import ScadaParams004


class ScadaParams002(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.params/002"""

    from_g_node_alias: LeftRightDot
    from_name: SpaceheatName
    to_name: SpaceheatName
    unix_time_ms: UTCMilliseconds
    message_id: UUID4Str
    new_params: Ha1Params001 | Ha1Params002 | Ha1Params003 | None = None
    old_params: Ha1Params001 | Ha1Params002 | Ha1Params003 | None = None
    type_name: Literal["scada.params"] = "scada.params"
    version: Literal["002"] = "002"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> ScadaParams004:
        """
        - NewParams: ha1.params:001 | ha1.params:002 | ha1.params:003 -> ha1.params:004
        - OldParams: ha1.params:001 | ha1.params:002 | ha1.params:003 -> ha1.params:004
        """
        data = self.model_dump()
        if self.new_params is not None:
            new_params: SemaType = self.new_params
            while new_params.version != "004":
                new_params = new_params.upgrade()
            data["new_params"] = new_params
        if self.old_params is not None:
            old_params: SemaType = self.old_params
            while old_params.version != "004":
                old_params = old_params.upgrade()
            data["old_params"] = old_params
        data["version"] = "004"
        return ScadaParams004.model_validate(data)
