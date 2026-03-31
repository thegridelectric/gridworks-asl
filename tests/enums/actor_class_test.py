"""
Tests for enum gw1.actor.class latest and old versions.
"""

from sema.registry.enums import Gw1ActorClass
from sema.registry.enums.old_versions import Gw1ActorClass009, Gw1ActorClass010


def test_gw1_actor_class_latest() -> None:
    assert set(Gw1ActorClass.values()) == {
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
        "I2cThermistorReader",
    }

    assert Gw1ActorClass.default() == Gw1ActorClass.NoActor
    assert Gw1ActorClass.enum_name() == "gw1.actor.class"
    assert Gw1ActorClass.enum_version() == "011"


def test_gw1_actor_class_010() -> None:
    assert set(Gw1ActorClass010.values()) == {
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
    assert Gw1ActorClass010.default() == Gw1ActorClass010.NoActor
    assert Gw1ActorClass010.enum_name() == "gw1.actor.class"
    assert Gw1ActorClass010.enum_version() == "010"


def test_gw1_actor_class_009() -> None:
    assert set(Gw1ActorClass009.values()) == {
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
    }
    assert Gw1ActorClass009.default() == Gw1ActorClass009.NoActor
    assert Gw1ActorClass009.enum_name() == "gw1.actor.class"
    assert Gw1ActorClass009.enum_version() == "009"
