from typing import Literal

from sema.runtime.base import SemaType
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt


class SimPicoTankModuleComponentGt(PicoTankModuleComponentGt):
    """Sema: https://schemas.electricity.works/types/sim.pico.tank.module.component.gt/000"""

    simulates_type_name: Literal["pico.tank.module.component.gt"] = "pico.tank.module.component.gt"
    simulates_version: Literal["011"] = "011"
    type_name: Literal["sim.pico.tank.module.component.gt"] = "sim.pico.tank.module.component.gt"
    version: Literal["000"] = "000"
