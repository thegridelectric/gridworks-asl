from sema.registry.types.layout_lite import LayoutLite
from runtime_sample_test_helpers import decode_runtime_payload


def test_runtime_sample_spruce_layout_lite() -> None:
    decoded = decode_runtime_payload(
        "gridworks-scada-jm-spruce/"
        "hw1.isone.me.versant.keene.spruce.scada-layout.lite-1774955735150-ear.electricity.works.json"
    )

    assert isinstance(decoded, LayoutLite)
    assert decoded.version == "012"
    assert decoded.type_name == "layout.lite"
