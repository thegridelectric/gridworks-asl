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
    """
    Checks that all dict keys are pascal case, all the way down
    """
    if isinstance(d, dict):
        # Check if all keys in the dictionary are in PascalCase
        for key, value in d.items():
            if not is_pascal_case(key):
                return False
            if not recursively_pascal(value):
                return False
    elif isinstance(d, list):
        # Recursively check if dictionaries or lists inside a list pass the test
        for item in d:
            if not recursively_pascal(item):
                return False
    # If it's neither a dict nor a list, return True (nothing to check)
    return True


def pascal_to_snake(name: str) -> str:
    return snake_add_underscore_to_camel_pattern.sub("_", name).lower()


def snake_to_pascal(word: str) -> str:
    return "".join(x.capitalize() or "_" for x in word.split("_"))


# ============================================================================
# BASE CLASS
# ============================================================================



class AslError(Exception):
    """Base exception for ASL-related errors."""


T = TypeVar("T", bound="AslType")

class AslType(BaseModel):
    """
    Base class for the Application Shared Language Types

    Notes:
        - `type_name`: Must follow left-right-dot (LRD) format. Subclasses
        are expected to overwrite this with a literal. The format is enforced
        by the ASL Type Registry , which is the source of truth
        - `version`: Must be  a three-digit string (e.g. "000", "001"), or None.
        Subclasses are expected to overwrite this with either a literal or a
        string, with the literal (strict versioning) being the default. The
        format is enforced by the ASL Type Registry, which is the source of truth.

    For more information:
      - [GridWorks ASL Docs](https://gridworks-asl.readthedocs.io)
    """

    type_name: str
    version: str | None = None

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        frozen=True,
        populate_by_name=True,
        extra="forbid",
    )

    def to_bytes(self) -> bytes:
        return self.model_dump_json(exclude_none=True, by_alias=True).encode()

    def to_dict(self) -> dict[str, Any]:
        json_bytes = self.model_dump_json(exclude_none=True, by_alias=True)
        return json.loads(json_bytes)

    @classmethod
    def from_bytes(cls, json_bytes: bytes) -> Self:
        try:
            d = json.loads(json_bytes)
        except TypeError as e:
            raise AslError("Type must be string or bytes!") from e
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        if not recursively_pascal(d):
            raise AslError(
                f"Dictionary keys must be recursively PascalCase. "
                f"Found: {d}. Consider checking nested structures."
            )
        try:
            t = cls.model_validate(d)
        except ValidationError as e:
            raise AslError(f"Validation failed for {cls.__name__}: {e}") from e
        return t

    @classmethod
    def get_schema_info(cls) -> dict[str, Any]:
        """Return schema information for this type."""
        return {
            "type_name": cls.type_name_value(),
            "version": cls.version_value(),
            "fields": list(cls.model_fields.keys()),
        }

    @classmethod
    def type_name_value(cls) -> str:
        # Automatically return the type_name defined in the subclass
        return cls.model_fields["type_name"].default

    @classmethod
    def version_value(cls) -> str | None:
        # return the Version defined in the subclass
        return cls.model_fields["version"].default

    def to_latest(self) -> "AslType":
        """
        Convert to the latest version of this type.

        Override this method in old version classes to provide
        migration logic to the current version.

        Raises:
            NotImplementedError: This is not an old version class
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement to_latest(). "
            "This method should only be called on old version types."
        )
