from pathlib import Path

import yaml

from sema.tools.build_seed_expanded import expand_seed
from sema.tools.runtime_generation.generate_runtime import generate_runtime_from_dag


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_runtime_generation_uses_local_enum_class_name(tmp_path: Path) -> None:
    registry = load_yaml(REPO_ROOT / "definitions" / "registry.yaml")
    seed_request = tmp_path / "seed_request.yaml"
    seed_request.write_text(
        "initial_targets:\n"
        "  types:\n"
        "    pico.flow.module.component.gt:\n"
        "      versions: [\"000\"]\n"
    )
    expanded_seed = tmp_path / "seed_expanded.yaml"
    expand_seed(seed_request, expanded_seed)
    seed = load_yaml(expanded_seed)
    local_names = {
        "types": {},
        "enums": {
            "spaceheat.make.model": {
                "local_class_name": "MakeModel",
            },
        },
        "formats": {},
    }

    target_root = tmp_path / "gjk" / "sema"
    generate_runtime_from_dag(
        target_root,
        seed,
        registry,
        REPO_ROOT / "definitions",
        "gjk",
        local_names,
    )

    enum_text = (target_root / "enums" / "make_model.py").read_text()
    type_text = (target_root / "types" / "pico_flow_module_component_gt.py").read_text()

    assert "class MakeModel(SemaEnum):" in enum_text
    assert "from gjk.sema.enums.make_model import MakeModel" in type_text
    assert "flow_meter_type: MakeModel" in type_text
