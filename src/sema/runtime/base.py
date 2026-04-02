import json
import re
from typing import Any, Self, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

snake_add_underscore_to_camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def is_pascal_case(s: str) -> bool:
    return re.match(r"^[A-Z][a-zA-Z0-9]*$", s) is not None


def recursively_pascal(d: dict) -> bool:
    if isinstance(d, dict):
        for key, value in d.items():
            if key and key[0].isalpha() and not is_pascal_case(key):
                return False
            if not recursively_pascal(value):
                return False
    elif isinstance(d, list):
        for item in d:
            if not recursively_pascal(item):
                return False
    return True


def pascal_to_snake(name: str) -> str:
    return snake_add_underscore_to_camel_pattern.sub("_", name).lower()


def snake_to_pascal(word: str) -> str:
    return "".join(x.capitalize() or "_" for x in word.split("_"))


# ============================================================================
# BASE EXCEPTIONS
# ============================================================================

class SemaError(Exception):
    """Base exception for Sema-related errors."""


T = TypeVar("T", bound="SemaType")


# ============================================================================
# STRICT SEMA TYPE
# ============================================================================

class SemaType(BaseModel):
    """
    Base class for strict Sema types.
    """

    type_name: str
    version: str | None = None

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        frozen=True,
        populate_by_name=True,
        extra="forbid",
    )

    # ------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------

    def to_bytes(self) -> bytes:
        return self.model_dump_json(exclude_none=True, by_alias=True).encode()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_bytes(cls, json_bytes: bytes) -> Self:
        try:
            d = json.loads(json_bytes)
        except TypeError as e:
            raise SemaError("Type must be string or bytes!") from e
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        if not recursively_pascal(d):
            raise SemaError("Dictionary must be recursively PascalCase")
        try:
            return cls.model_validate(d)
        except ValidationError as e:
            raise SemaError(f"Validation failed: {e}") from e

    # ------------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------------

    @classmethod
    def type_name_value(cls) -> str:
        return cls.model_fields["type_name"].default

    @classmethod
    def version_value(cls) -> str | None:
        return cls.model_fields["version"].default

    # ------------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------------

    def upgrade(self) -> "SemaType":
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement upgrade()"
        )

    def to_latest(self, registry: dict[str, type["SemaType"]]) -> "SemaType":
        current = self
        type_name = self.type_name_value()

        if type_name not in registry:
            raise SemaError(f"No registry entry for {type_name}")

        latest_cls = registry[type_name]
        latest_version = latest_cls.version_value()

        safety = 0
        while current.version != latest_version:
            safety += 1
            if safety > 20:
                raise SemaError("Upgrade loop detected")
            current = current.upgrade()

        return current


# ============================================================================
# DEGRADED TYPE
# ============================================================================

class DegradedSemaType:
    """
    Best-effort decoded Sema-like object.

    This is NOT a valid SemaType and MUST NOT be used for control logic.
    """

    def __init__(
        self,
        *,
        type_name: str,
        version: str | None,
        raw: dict[str, Any],
        known_fields: dict[str, Any],
        unknown_fields: dict[str, Any],
    ):
        self.type_name = type_name
        self.version = version
        self.raw = raw
        self.known_fields = known_fields
        self.unknown_fields = unknown_fields

    def to_dict(self) -> dict[str, Any]:
        return self.raw