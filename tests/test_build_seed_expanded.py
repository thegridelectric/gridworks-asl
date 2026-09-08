from pathlib import Path

import pytest
import yaml

from sema.tools.build_seed_expanded import expand_seed


def expand_request(tmp_path: Path, request: str) -> dict:
    request_path = tmp_path / "seed_request.yaml"
    output_path = tmp_path / "seed_expanded.yaml"
    request_path.write_text(request)
    expand_seed(request_path, output_path)
    return yaml.safe_load(output_path.read_text())


def test_structured_seed_request_uses_latest_for_empty_options(tmp_path: Path) -> None:
    expanded = expand_request(
        tmp_path,
        """
initial_targets:
  types:
    layout.lite: {}
""",
    )

    assert expanded["initial_targets"] == ["layout.lite:013"]
    assert "013" in expanded["worklist"]["types"]["layout.lite"]


def test_structured_seed_request_adds_intermediate_type_versions(tmp_path: Path) -> None:
    expanded = expand_request(
        tmp_path,
        """
initial_targets:
  types:
    layout.lite:
      versions: ["011", "013"]
""",
    )

    assert expanded["initial_targets"] == ["layout.lite:011", "layout.lite:013"]
    assert {"011", "012", "013"} <= set(expanded["worklist"]["types"]["layout.lite"])


def test_include_all_versions_uses_public_versions_only(tmp_path: Path) -> None:
    expanded = expand_request(
        tmp_path,
        """
initial_targets:
  types:
    fsm.atomic.report:
      include_all_versions: true
""",
    )

    assert expanded["initial_targets"] == ["fsm.atomic.report:000", "fsm.atomic.report:001"]
    assert set(expanded["worklist"]["types"]["fsm.atomic.report"]) == {"000", "001"}
    assert "002" not in expanded["worklist"]["types"]["fsm.atomic.report"]


def test_structured_seed_request_accepts_enum_versions(tmp_path: Path) -> None:
    expanded = expand_request(
        tmp_path,
        """
initial_targets:
  enums:
    relay.energization.state:
      versions: ["000"]
""",
    )

    assert expanded["initial_targets"] == ["relay.energization.state:000"]
    assert "000" in expanded["worklist"]["enums"]["relay.energization.state"]


def test_structured_seed_request_rejects_formats_section(tmp_path: Path) -> None:
    request_path = tmp_path / "seed_request.yaml"
    output_path = tmp_path / "seed_expanded.yaml"
    request_path.write_text(
        """
initial_targets:
  formats:
    left.right.dot: {}
"""
    )

    with pytest.raises(ValueError, match="types and enums"):
        expand_seed(request_path, output_path)
