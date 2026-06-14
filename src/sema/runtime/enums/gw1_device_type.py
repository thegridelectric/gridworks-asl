from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1DeviceType(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.device.type/000"""

    UnknownDeviceType = auto()
    EgaugePowerMeter = auto()
    GridworksTsnap1ScadaBoard = auto()
    GridworksSimPowerMeter = auto()
    HubitatC7Hub = auto()
    Amphenol10kThermistor = auto()
    OmegaFtb8010FlowMeter = auto()
    HoneywellT6Thermostat = auto()
    TewaThermistor = auto()
    EkmFlowMeter = auto()
    GridworksSimMultiTemp = auto()
    KridaDoubleRelayBoard16 = auto()
    GridworksPicoFlowHall = auto()
    GridworksPicoFlowReed = auto()
    SaierFlowSensor = auto()
    DfrobotDualAnalogOut = auto()
    GridworksTankModule3 = auto()
    GridworksGw101 = auto()
    GridworksScadaGw108 = auto()
    GridworksSimSensor = auto()
    GridworksSimRelayBank = auto()

    @classmethod
    def default(cls) -> "Gw1DeviceType":
        return cls.UnknownDeviceType

    @classmethod
    def values(cls) -> list[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw1.device.type"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
