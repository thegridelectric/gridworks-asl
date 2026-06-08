"""gjk-fix by removal: a snapshot seeded with bid has a self-contained slot format.

The de-tangled market.slot.name validates structure only — it no longer reaches
an enum (no MarketTypeName check), so a restricted consumer snapshot seeding bid
generates a property_format.py with no enum import in the slot validator. The
ModuleNotFoundError class that motivated the untangle is gone by removal of the
hidden format->enum edge, while bid/latest.price stay uniform across makers.
"""

from pathlib import Path

from sema.interfaces.cli import snapshot
from sema.tools.build_public_registry import build_public_registry, load_registry


ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_with_bid_has_self_contained_slot_format(monkeypatch, tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    monkeypatch.setattr(snapshot, "OUTPUT_DIR", output_root)
    monkeypatch.setattr(
        snapshot,
        "build_public_registry_index",
        lambda: build_public_registry(load_registry()),
    )

    seed_request = tmp_path / "seed.yaml"
    seed_request.write_text("initial_targets:\n  types:\n    bid: {}\n")

    snapshot.prepare_snapshot(seed_request)
    target_root = snapshot.build_snapshot_runtime("gjk")

    pf = (target_root / "property_format.py").read_text()
    # The slot validator is present and self-contained.
    assert "def is_market_slot_name(" in pf
    # No hidden format->enum edge: the slot validator pulls in no enum.
    assert "MarketTypeName" not in pf
    assert ".enums import" not in pf
    # No product enum is dragged into the bid snapshot.
    assert not (target_root / "enums" / "gw_market_product_name.py").exists()
