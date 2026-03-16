"""
Tests for enum spaceheat.make.model.004
"""

from sema.registry.enums import MakeModel


def test_make_model() -> None:
    assert set(MakeModel.values()) == {
        "UNKNOWNMAKE__UNKNOWNMODEL",
        "EGAUGE__4030",
        "NCD__PR814SPST",
        "ADAFRUIT__642",
        "GRIDWORKS__TSNAP1",
        "GRIDWORKS__WATERTEMPHIGHPRECISION",
        "GRIDWORKS__SIMPM1",
        "SCHNEIDERELECTRIC__IEM3455",
        "GRIDWORKS__SIMBOOL30AMPRELAY",
        "OPENENERGY__EMONPI",
        "GRIDWORKS__SIMTSNAP1",
        "ATLAS__EZFLO",
        "HUBITAT__C7__LAN1",
        "GRIDWORKS__TANK_MODULE_1",
        "FIBARO__ANALOG_TEMP_SENSOR",
        "AMPHENOL__NTC_10K_THERMISTOR_MA100GG103BN",
        "YHDC__SCT013100",
        "MAGNELAB__SCT0300050",
        "GRIDWORKS__MULTITEMP1",
        "KRIDA__EMR16I2CV3",
        "OMEGA__FTB8007HWPT",
        "ISTEC_4440",
        "OMEGA__FTB8010HWPT",
        "BELIMO__BALLVALVE232VS",
        "BELIMO__DIVERTERB332L",
        "TACO__0034EPLUS",
        "TACO__007E",
        "ARMSTRONG__COMPASSH",
        "HONEYWELL__T6ZWAVETHERMOSTAT",
        "PRMFILTRATION__WM075",
        "BELLGOSSETT__ECOCIRC20_18",
        "TEWA__TT0P10KC3T1051500",
        "EKM__HOTSPWM075HD",
        "GRIDWORKS__SIMMULTITEMP",
        "GRIDWORKS__SIMTOTALIZER",
        "KRIDA__DOUBLEEMR16I2CV3",
        "GRIDWORKS__SIMDOUBLE16PINI2CRELAY",
        "GRIDWORKS__TANKMODULE2",
        "GRIDWORKS__PICOFLOWHALL",
        "GRIDWORKS__PICOFLOWREED",
        "SAIER__SENHZG1WA",
        "DFROBOT__DFR0971_TIMES2",
    }

    assert MakeModel.default() == MakeModel.UNKNOWNMAKE__UNKNOWNMODEL
    assert MakeModel.enum_name() == "spaceheat.make.model"
    assert MakeModel.enum_version() == "004"

