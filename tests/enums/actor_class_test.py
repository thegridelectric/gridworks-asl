"""
Tests for enum gw1.actor.class.010
"""

from sema.registry.enums import ActorClass


def test_actor_class() -> None:
    assert set(ActorClass.values()) == {
        "NoActor",
        "PrimaryScada",
        "SecondaryScada",
        "PowerMeter",
        "LocalControl",
        "LeafAlly",
        "DerivedGenerator",
        "PicoCycler",
        "HpBoss",
        "I2cRelayMultiplexer",
        "I2cZeroTenMultiplexer",
        "Hubitat",
        "Relay",
        "MultipurposeSensor",
        "HoneywellThermostat",
        "ApiTankModule",
        "ApiFlowModule",
        "ZeroTenOutputer",
        "ApiBtuMeter",
        "SiegLoop",
        "GpioSensor",
        "I2cBus",
        "I2cRelayBoard",
    }

    assert ActorClass.default() == ActorClass.NoActor
    assert ActorClass.enum_name() == "gw1.actor.class"
    assert ActorClass.enum_version() == "010"
