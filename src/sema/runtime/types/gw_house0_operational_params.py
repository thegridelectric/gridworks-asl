from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.types.capture_tuning import CaptureTuning
from sema.runtime.types.g_node_gt import GNodeGt


class GwHouse0OperationalParams(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.house0.operational.params/000"""

    g_nodes: list[GNodeGt]
    capture_tuning_list: list[CaptureTuning]
    type_name: Literal["gw.house0.operational.params"] = "gw.house0.operational.params"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwHouse0OperationalParams":
        """
        Axiom 1: CaptureTuningChannelUniqueness
        ChannelName SHALL be unique across CaptureTuningList.
        """
        names = [ct.channel_name for ct in self.capture_tuning_list]
        if len(names) != len(set(names)):
            raise ValueError(
                "Axiom 1 (CaptureTuningChannelUniqueness) failed: ChannelName "
                "must be unique across CaptureTuningList."
            )
        return self
