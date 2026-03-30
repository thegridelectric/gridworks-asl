"""
Tests for enum g.node.class.000
"""

from sema.registry.enums import GNodeClass


def test_g_node_class() -> None:
    assert set(GNodeClass.values()) == {
        "Unknown",
        "TerminalAsset",
        "LeafTransactiveNode",
        "ConnectivityNode",
        "MarketMaker",
        "Scada",
        "AggregatedTNode",
        "PriceForecastService",
        "WeatherForecastService",
        "TimeCoordinator",
    }

    assert GNodeClass.default() == GNodeClass.Unknown
    assert GNodeClass.enum_name() == "g.node.class"
    assert GNodeClass.enum_version() == "000"
