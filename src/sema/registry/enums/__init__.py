"""
Sema enum definitions for Grid Node Registry

Enums define versioned controlled vocabularies used at system boundaries.
They evolve additively (values may be added but not removed or reordered)
to preserve backward compatibility across distributed systems.

All enums correspond to published Sema schemas under:
https://schemas.electricity.works/enums/
"""

from sema.registry.enums.base_g_node_class import BaseGNodeClass
from sema.registry.enums.change_relay_state import ChangeRelayState
from sema.registry.enums.fis_authorization_decision import FisAuthorizationDecision
from sema.registry.enums.fis_authorization_reason import FisAuthorizationReason
from sema.registry.enums.g_node_class import GNodeClass
from sema.registry.enums.g_node_instance_status import GNodeInstanceStatus
from sema.registry.enums.g_node_instance_transport import GNodeInstanceTransport
from sema.registry.enums.g_node_status import GNodeStatus
from sema.registry.enums.gpm_from_hz_method import GpmFromHzMethod
from sema.registry.enums.gw0_representation_status import Gw0RepresentationStatus
from sema.registry.enums.gw1_actor_class import Gw1ActorClass
from sema.registry.enums.gw1_emission_method import Gw1EmissionMethod
from sema.registry.enums.gw1_float_unit import Gw1FloatUnit
from sema.registry.enums.gw1_quantity import Gw1Quantity
from sema.registry.enums.gw1_seasonal_storage_mode import Gw1SeasonalStorageMode
from sema.registry.enums.gw1_system_mode import Gw1SystemMode
from sema.registry.enums.gw1_unit import Gw1Unit
from sema.registry.enums.hz_calc_method import HzCalcMethod
from sema.registry.enums.message_category import MessageCategory
from sema.registry.enums.message_category_symbol import MessageCategorySymbol
from sema.registry.enums.market_quantity_unit import MarketQuantityUnit
from sema.registry.enums.market_price_unit import MarketPriceUnit
from sema.registry.enums.market_type_name import MarketTypeName
from sema.registry.enums.recognized_currency_unit import RecognizedCurrencyUnit
from sema.registry.enums.relay_closed_or_open import RelayClosedOrOpen
from sema.registry.enums.relay_wiring_config import RelayWiringConfig
from sema.registry.enums.spaceheat_make_model import SpaceheatMakeModel
from sema.registry.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.registry.enums.spaceheat_unit import SpaceheatUnit
from sema.registry.enums.temp_calc_method import TempCalcMethod


__all__ = [
    "BaseGNodeClass",
    "ChangeRelayState",
    "FisAuthorizationDecision",
    "FisAuthorizationReason",
    "GNodeClass",
    "GNodeInstanceStatus",
    "GNodeInstanceTransport",
    "GNodeStatus",
    "GpmFromHzMethod",
    "Gw0RepresentationStatus",
    "Gw1ActorClass",
    "Gw1EmissionMethod",
    "Gw1FloatUnit",
    "Gw1Quantity",
    "Gw1SeasonalStorageMode",
    "Gw1SystemMode",
    "Gw1Unit",
    "HzCalcMethod",
    "MessageCategory",
    "MessageCategorySymbol",
    "MarketPriceUnit",
    "MarketQuantityUnit",
    "MarketTypeName",
    "RecognizedCurrencyUnit",
    "RelayClosedOrOpen",
    "RelayWiringConfig",
    "SpaceheatMakeModel",
    "SpaceheatTelemetryName",
    "SpaceheatUnit",
    "TempCalcMethod",
]
