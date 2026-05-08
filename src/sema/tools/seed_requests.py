from __future__ import annotations

def build_all_registry_seed_request(registry: dict) -> dict:
    return {
        "initial_targets": {
            "types": {
                name: {"include_all_versions": True}
                for name in sorted(registry["types"])
            },
            "enums": {
                name: {"include_all_versions": True}
                for name in sorted(registry["enums"])
            },
        }
    }


def expand_all_registry_seed(_tmp_path, registry: dict) -> dict:
    seed = {
        "metadata": {
            "generated_from": "provided registry",
            "note": "All entries from the supplied registry",
        },
        "initial_targets": [],
        "worklist": {
            "formats": {},
            "enums": {},
            "types": {},
        },
    }

    for format_name in sorted(registry["formats"]):
        seed["worklist"]["formats"][format_name] = {
            "path": f"definitions/formats/{format_name}.yaml"
        }

    for enum_name, entry in sorted(registry["enums"].items()):
        seed["initial_targets"].append(enum_name)
        seed["worklist"]["enums"][enum_name] = {}
        if entry["enum_type"] == "literal":
            seed["worklist"]["enums"][enum_name]["000"] = {
                "path": f"definitions/enums/{enum_name}/000.yaml"
            }
            continue
        for version in sorted(entry.get("versions", {}), key=int):
            seed["worklist"]["enums"][enum_name][version] = {
                "path": f"definitions/enums/{enum_name}/{version}.yaml"
            }

    for type_name, entry in sorted(registry["types"].items()):
        seed["initial_targets"].append(type_name)
        if entry["versioning_strategy"] == "none":
            seed["worklist"]["types"][type_name] = {
                "versioning_strategy": "none",
                "path": f"definitions/types/{type_name}.yaml",
            }
            continue
        seed["worklist"]["types"][type_name] = {}
        for version in sorted(entry.get("versions", {}), key=int):
            seed["worklist"]["types"][type_name][version] = {
                "path": f"definitions/types/{type_name}/{version}.yaml"
            }

    return seed
