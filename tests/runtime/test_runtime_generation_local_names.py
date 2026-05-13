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
        "spaceheat.make.model": "make.model",
    }

    target_root = tmp_path / "gjk" / "sema"
    generate_runtime_from_dag(
        target_root,
        seed,
        registry,
        import_root="gjk.sema",
        local_names=local_names,
    )

    enum_text = (target_root / "enums" / "make_model.py").read_text()
    enum_init_text = (target_root / "enums" / "__init__.py").read_text()
    type_text = (target_root / "types" / "pico_flow_module_component_gt.py").read_text()

    assert "class MakeModel(SemaEnum):" in enum_text
    assert "from gjk.sema.enums.make_model import MakeModel" in enum_init_text
    assert "from gjk.sema.enums import MakeModel" in type_text
    assert "\n\n\nclass PicoFlowModuleComponentGt(SemaType):" in type_text
    assert "flow_meter_type: MakeModel" in type_text


def test_runtime_generation_allows_extra_fields_only_for_additional_properties_true(
    tmp_path: Path,
) -> None:
    registry = load_yaml(REPO_ROOT / "definitions" / "registry.yaml")
    seed_request = tmp_path / "seed_request.yaml"
    seed_request.write_text(
        "initial_targets:\n"
        "  types:\n"
        "    fsm.full.report:\n"
        "      versions: [\"001\"]\n"
        "    channel.config:\n"
        "      versions: [\"000\"]\n"
    )
    expanded_seed = tmp_path / "seed_expanded.yaml"
    expand_seed(seed_request, expanded_seed)
    seed = load_yaml(expanded_seed)

    target_root = tmp_path / "gjk" / "sema"
    generate_runtime_from_dag(
        target_root,
        seed,
        registry,
        import_root="gjk.sema",
    )

    extra_allowed_text = (target_root / "types" / "fsm_full_report.py").read_text()
    extra_forbidden_text = (target_root / "types" / "channel_config.py").read_text()

    assert "from pydantic import ConfigDict" in extra_allowed_text
    assert (
        '    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))'
    ) in extra_allowed_text

    assert "ConfigDict" not in extra_forbidden_text
    assert 'extra="allow"' not in extra_forbidden_text
