from enum import auto

from sema.runtime.enums.gw_str_enum import SemaEnum


class Gw1DeviceType(SemaEnum):
    """Sema: https://schemas.electricity.works/enums/gw1.device.type/000"""

    UnknownDeviceType = auto()
    EgaugePowerMeter = auto()
    NcdRelayBoard = auto()
    AdafruitWaterproofTempSensor = auto()
    GridworksTsnap1ScadaBoard = auto()
    GridworksHighPrecisionWaterTemp = auto()
    GridworksSimPowerMeter = auto()
    SchneiderPowerMeter = auto()
    GridworksSim30AmpRelay = auto()
    OpenenergyEmonPi = auto()
    GridworksSimTsnap1 = auto()
    AtlasEzfloFlowMeter = auto()
    HubitatC7Hub = auto()
    GridworksTankModule1 = auto()
    FibaroAnalogTempSensor = auto()
    Amphenol10kThermistor = auto()
    YhdcCurrentTransformer = auto()
    MagnelabCurrentTransformer = auto()
    GridworksMultiTemp1 = auto()
    KridaRelayBoard16 = auto()
    OmegaFtb8007FlowMeter = auto()
    IstecFlowMeter = auto()
    OmegaFtb8010FlowMeter = auto()
    BelimoBallValve = auto()
    BelimoDiverterValve = auto()
    Taco0034Pump = auto()
    Taco007Pump = auto()
    ArmstrongCompassHPump = auto()
    HoneywellT6Thermostat = auto()
    PrmFlowMeter = auto()
    BellGossettEcocircPump = auto()
    TewaThermistor = auto()
    EkmFlowMeter = auto()
    GridworksSimMultiTemp = auto()
    GridworksSimTotalizer = auto()
    KridaDoubleRelayBoard16 = auto()
    GridworksSimDouble16PinRelay = auto()
    GridworksTankModule2 = auto()
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
