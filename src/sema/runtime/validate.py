"""Validate a serialized payload against the Sema vocabulary.

Decoding a payload through the Sema runtime *is* the validation: a clean decode
means it conforms to its declared type's schema — field shapes, property formats,
axioms, and version. This module wraps that in a structured result (rather than a
raised exception) so callers — the CLI, round-trip harnesses, conformance sweeps —
can branch on `.ok` and report `.error`.

Sema is the source of truth, so this validates against the canonical runtime
(`sema.runtime.codec.default_codec`), not a downstream codegen'd copy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from sema.runtime.codec import default_codec


@dataclass
class ValidationResult:
    ok: bool
    type_name: str | None = None
    version: str | None = None
    error: str | None = None


def validate(data: dict | str | bytes, *, expected_type: str | None = None) -> ValidationResult:
    """Validate `data` (a dict or JSON text) against the Sema vocabulary.

    Returns a `ValidationResult`. On success, `type_name`/`version` reflect the
    decoded (post-upgrade) type. If `expected_type` is given and the decoded
    `TypeName` differs, the result is not ok.
    """
    parsed: object = data
    try:
        if isinstance(data, (str, bytes)):
            parsed = json.loads(data)
        if not isinstance(parsed, dict):
            return ValidationResult(ok=False, error="Payload is not a JSON object.")
        decoded_tn = parsed.get("TypeName")
        obj = default_codec.from_dict(parsed)
        type_name = getattr(obj, "type_name", None) or decoded_tn
        version = getattr(obj, "version", None) or parsed.get("Version")
        if expected_type is not None and type_name != expected_type:
            return ValidationResult(
                ok=False,
                type_name=type_name,
                version=version,
                error=f"Expected TypeName {expected_type!r}, got {type_name!r}.",
            )
        return ValidationResult(ok=True, type_name=type_name, version=version)
    except Exception as e:  # noqa: BLE001 — report any decode/validation failure
        tn = parsed.get("TypeName") if isinstance(parsed, dict) else None
        return ValidationResult(ok=False, type_name=tn, error=f"{type(e).__name__}: {e}")
