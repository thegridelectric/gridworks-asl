import json
import logging
from collections import defaultdict

from pydantic import ValidationError

from gwasl.registry.base import SemaError, SemaType, pascal_to_snake, snake_to_pascal

logger = logging.getLogger(__name__)



# ============================================================================
# CODEC CLASS
# ============================================================================

class SemaCodec:
    """
    Codec for this repository's Sema types.
    Handles version flexibility and naming convention conversion.
    """

    def __init__(self) -> None:
        """
        Initialize the codec with auto-discovered types
        """
        self.registry = get_current_types()
        self.old_versions = get_old_versions()

        # Validate that all old versions have a current target
        for type_name in self.old_versions:
            if type_name not in self.registry:
                raise ValueError(
                    f"Old versions found for '{type_name}' but no current version exists. "
                    f"Old versions: {list(self.old_versions[type_name].keys())}"
                )

    def from_dict(self, data: dict) -> SemaType:
        """Decode a dictionary to the appropriate SemaType."""
        type_name = data.get("TypeName")
        if not type_name:
            raise ValueError("Missing TypeName field")

        version = data.get("Version")

        if type_name not in self.registry:
            raise ValueError(
                f"Unknown type: {type_name}. "
                f"Known types: {self.registry.keys()}"
            )

        current_cls = self.registry[type_name]
        current_version = current_cls.version_value()

        # Fast path: version matches current
        if version == current_version:
            return current_cls.from_dict(data)

        # Translation path: we have an old version
        if type_name in self.old_versions and version in self.old_versions[type_name]:
            logger.warning(
                "Translating %s from v%s to v%s",
                type_name,
                version,
                current_version,
            )
            old_cls = self.old_versions[type_name][version]
            old_instance = old_cls.from_dict(data)
            return old_instance.to_latest()

        # Fallback: try to decode with current version anyway
        logger.warning(
            "Unknown version %s for %s, attempting decode with current v%s",
            version,
            type_name,
            current_version,
        )

        data = dict(data)  # Make a copy
        data["Version"] = current_version
        try:
            return current_cls.from_dict(data)
        except (ValidationError, SemaError):
            logger.warning("Stripping unknown fields and retrying")
            data = self._strip_unknown_fields(data, current_cls)
            return current_cls.from_dict(data)


    def from_bytes(self, data: bytes) -> SemaType:
        """Decode JSON bytes to the appropriate SemaType"""
        try:
            d = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Invalid JSON data: {e}") from e
        return self.from_dict(d)

    def to_bytes(self, msg: SemaType) -> bytes:
        """Encode an SemaType to JSON bytes"""
        return msg.to_bytes()

    def _strip_unknown_fields(self, data: dict, cls: type[SemaType]) -> dict:
        """Remove fields not recognized by the target class."""
        valid_fields = set()
        for field_name, field_info in cls.model_fields.items():
            valid_fields.add(field_name)
            valid_fields.add(snake_to_pascal(field_name))
            if field_info.alias:
                valid_fields.add(field_info.alias)

        return {
            key: value
            for key, value in data.items()
            if key in valid_fields or pascal_to_snake(key) in valid_fields
        }



# ============================================================================
# AUTO-DISCOVERY OF TYPES IN THIS REPO
# ============================================================================

def get_current_types() -> dict[str, type[SemaType]]:
    """
    Returns the types declared in `sema/types/__init__.py`
    """
    from gwasl.registry import types # noqa PLC0415
    registry = {}
    for name in types.__all__:
        cls = getattr(types, name)
        type_name = cls.type_name_value()
        registry[type_name] = cls

    return registry

def get_old_versions() -> dict[str, dict[str | None, type[SemaType]]]:
    """
     Returns a registry of old versions organized by type_name and version.
    Structure: {type_name: {version: class}}
    """
    from gwasl.registry.types import old_versions # noqa PLC0415
    old_types = [getattr(old_versions, name) for name in old_versions.__all__]

    old_registry: dict[str, dict[str | None, type[SemaType]]] = defaultdict(dict)

    for cls in old_types:
        type_name = cls.type_name_value()
        version = cls.version_value() # Could be None

        if type_name in old_registry and version in old_registry[type_name]:
            existing = old_registry[type_name][version]
            if existing != cls:
                raise ValueError(
                    f"Duplicate registration: {type_name} v{version} "
                    f"already registered to {existing.__name__}"
                )

        old_registry[type_name][version] = cls

    return old_registry

# ============================================================================
# DEFAULT CODEC INSTANCE FOR THIS REPOSITORY
# ============================================================================

# Create a default codec instance that can be imported
default_codec = SemaCodec()
