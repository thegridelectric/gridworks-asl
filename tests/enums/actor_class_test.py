"""
Tests for enum sh.actor.class.007
"""

from gwasl.registry.enums import ActorClass


def test_actor_class() -> None:
    assert set(ActorClass.values()) == {
        "NoActor",
        "Scada",
        "HomeAlone",
        "BooleanActuator",
        "PowerMeter",
        "Atn",
        "SimpleSensor",
        "MultipurposeSensor",
        "Thermostat",
        "HubitatTelemetryReader",
        "HubitatTankModule",
        "HubitatPoller",
        "I2cRelayMultiplexer",
        "FlowTotalizer",
        "Relay",
        "Admin",
        "Fsm",
        "Parentless",
        "Hubitat",
        "HoneywellThermostat",
        "ApiTankModule",
        "ApiFlowModule",
        "PicoCycler",
        "I2cDfrMultiplexer",
        "ZeroTenOutputer",
        "AtomicAlly",
        "SynthGenerator",
        "FakeAtn",
        "PumpDoctor",
        "StratBoss",
        "HpRelayBoss",
        "SiegLoop",
        "HpBoss",
    }

    assert ActorClass.default() == ActorClass.NoActor
    assert ActorClass.enum_name() == "sh.actor.class"
    assert ActorClass.enum_version() == "007"

