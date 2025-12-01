"""
Enums available in the GridWorks Application Shared Languages (ASL)

GridWorks ASL enables peer-to-peer shared vocabulary between energy system actors like 
SCADA devices, trading nodes, and market makers. Enums serve as the "controlled vocabulary" 
foundation that ensures everyone speaks the same language.

Key characteristics:
 - Immutable evolution: Enum values can be added but never changed or removed, ensuring 
   backwards compatibility across distributed systems
 - Transport-agnostic: Same enums work with RabbitMQ, HTTP APIs, Kafka, or any message delivery
 - Organizational autonomy: Each organization can build exactly the sophistication they need
   on top of shared foundations
 - Constitutional governance: Follow naming conventions (left.right.dot format) and 
   ownership rules defined in the ASL registry

Enums are the semantic building blocks that enable organizations to collaborate without 
compromising their independence. Unlike APIs where one party controls the vocabulary, 
ASL enums evolve through community governance while maintaining stability.

Application Shared Languages represent an evolution beyond traditional APIs - enabling 
true peer-to-peer collaboration where organizations maintain autonomy while sharing 
vocabulary, rather than client/server relationships where one party dictates the interface.

For more information:
 - [Why GridWorks ASL Exists](https://gridworks-asl.readthedocs.io/motivation/)
 - [ASL Rules and Guidelines](https://gridworks-asl.readthedocs.io/rules-and-guidelines/) 
 - [GridWorks ASL Overview](https://gridworks-asl.readthedocs.io/)
"""

from gwasl.registry.enums.actor_class import ActorClass
from gwasl.registry.enums.base_g_node_class import BaseGNodeClass
from gwasl.registry.enums.g_node_class import GNodeClass
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
    "GNodeClass",
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
