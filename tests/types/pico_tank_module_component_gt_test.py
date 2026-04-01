from pydantic import ValidationError

from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt


def test_pico_tank_module_component_gt_xor() -> None:
    try:
        PicoTankModuleComponentGt(
            component_id=str(__import__("uuid").uuid4()),
            component_attribute_class_id=str(__import__("uuid").uuid4()),
            config_list=[],
            enabled=True,
            pico_hw_uid="pico_abcdef",
            pico_a_hw_uid="pico_a",
            pico_b_hw_uid="pico_b",
            temp_calc_method="SimpleBeta",
            thermistor_beta=10,
            send_micro_volts=True,
            samples=1,
            num_sample_averages=1,
            serial_number="abc",
            async_capture_delta_micro_volts=1,
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
