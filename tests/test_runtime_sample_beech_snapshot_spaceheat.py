from sema.registry.types.snapshot_spaceheat import SnapshotSpaceheat
from runtime_sample_test_helpers import decode_runtime_payload


def test_runtime_sample_beech_snapshot_spaceheat() -> None:
    decoded = decode_runtime_payload(
        "gridworks-scada-dev/"
        "hw1.isone.me.versant.keene.beech.scada-snapshot.spaceheat-1774915200638-ear.electricity.works.json"
    )

    assert isinstance(decoded, SnapshotSpaceheat)
    assert decoded.version == "003"
    assert decoded.type_name == "snapshot.spaceheat"
