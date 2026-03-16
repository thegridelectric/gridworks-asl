"""
Tests for enum g.node.class.000
"""

from sema.registry.enums import GNodeClass


def test_g_node_class() -> None:
    assert set(GNodeClass.values()) == {
        "GNode",
        "TerminalAsset",
        "Scada",
        "LeafTransactiveNode",
        "MarketMaker",
        "PriceService",
        "WeatherService",
    }

    assert GNodeClass.default() == GNodeClass.GNode
    assert GNodeClass.enum_name() == "g.node.class"
    assert GNodeClass.enum_version() == "000"

