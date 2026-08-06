from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonEmptyString
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds


class GwExperimentRun(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.experiment.run/000"""

    experiment_slug: SpaceheatName
    host_g_node_alias: LeftRightDot
    start_unix_ms: UTCMilliseconds
    end_unix_ms: UTCMilliseconds
    code_ref: NonEmptyString | None = None
    type_name: Literal["gw.experiment.run"] = "gw.experiment.run"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwExperimentRun":
        """
        Axiom 1: TimeOrder
        EndUnixMs SHALL be greater than StartUnixMs.
        """
        if not self.end_unix_ms > self.start_unix_ms:
            raise ValueError(
                "Axiom 1 (TimeOrder) failed: EndUnixMs must be greater than "
                "StartUnixMs."
            )
        return self
