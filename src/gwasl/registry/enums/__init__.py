"""
Sema enum definitions for Grid Node Registry

Enums define versioned controlled vocabularies used at system boundaries.
They evolve additively (values may be added but not removed or reordered)
to preserve backward compatibility across distributed systems.

All enums correspond to published Sema schemas under:
https://schemas.electricity.works/enums/
"""

from gwasl.registry.enums.actor_class import ActorClass
from gwasl.registry.enums.base_g_node_class import BaseGNodeClass
from gwasl.registry.enums.fis_authorization_decision import FisAuthorizationDecision
from gwasl.registry.enums.fis_authorization_reason import FisAuthorizationReason
from gwasl.registry.enums.g_node_class import GNodeClass
from gwasl.registry.enums.g_node_instance_status import GNodeInstanceStatus
from gwasl.registry.enums.g_node_instance_transport import GNodeInstanceTransport
from gwasl.registry.enums.g_node_status import GNodeStatus
from gwasl.registry.enums.gw0_representation_status import Gw0RepresentationStatus
from gwasl.registry.enums.make_model import MakeModel
from gwasl.registry.enums.message_category import MessageCategory
from gwasl.registry.enums.message_category_symbol import MessageCategorySymbol
from gwasl.registry.enums.market_quantity_unit import MarketQuantityUnit
from gwasl.registry.enums.market_price_unit import MarketPriceUnit
from gwasl.registry.enums.market_type_name import MarketTypeName
from gwasl.registry.enums.recognized_currency_unit import RecognizedCurrencyUnit
from gwasl.registry.enums.relay_closed_or_open import RelayClosedOrOpen
from gwasl.registry.enums.telemetry_name import TelemetryName


__all__ = [
    "ActorClass",
    "BaseGNodeClass",
    "FisAuthorizationDecision",
    "FisAuthorizationReason",
    "GNodeClass",
    "GNodeInstanceStatus",
    "GNodeInstanceTransport",
    "GNodeStatus",
    "Gw0RepresentationStatus",
    "MakeModel",
    "MessageCategory",
    "MessageCategorySymbol",
    "MarketPriceUnit",
    "MarketQuantityUnit",
    "MarketTypeName",
    "RecognizedCurrencyUnit",
    "RelayClosedOrOpen",
    "TelemetryName",
]
