"""Lint gate for a generated Sema runtime tree.

Applied to the *staged* snapshot tree before the atomic swap. Two tiers:

- ``ruff format`` — applied **in place**. The generator already sorts its
  output (imports, ``topo_sort``), so formatting is the last source of churn;
  running it here makes a second regen produce a zero diff. This always runs.
- ``ruff check`` + ``mypy`` — run as **gates** that signal *generator* bugs
  (dirty generated code). They are reported every build. They become fatal only
  under ``strict=True`` because the generator currently emits a small set of
  known violations (over-/under-tracked ``typing`` imports; pydantic/enum
  dynamics mypy can't follow) that are a separate cleanup; until that lands,
  a non-strict build reports them without blocking. See
  ``wiki/sema/changelog.md`` / the snapshot spec for the tracked follow-up.

Reuses sema's own ruff/mypy (the repo config), invoked via the interpreter
running the build so the toolchain matches the source repo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class LintGateError(RuntimeError):
    """A hard lint gate failed; the staged snapshot SHALL NOT be swapped in."""


def _run(tool_args: list[str], target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", *tool_args, str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def format_in_place(target: Path) -> None:
    """Run ``ruff format`` over the tree. Raises only on a ruff invocation error."""
    result = _run(["ruff", "format"], target)
    if result.returncode != 0:
        raise LintGateError(f"ruff format failed:\n{result.stdout}\n{result.stderr}")


def lint_generated_tree(target: Path, *, strict: bool = False) -> list[str]:
    """Format in place, then run ruff check + mypy.

    Returns the list of human-readable gate violations (empty when clean). When
    ``strict`` and violations exist, raises :class:`LintGateError` so the caller
    aborts before touching the previous snapshot.
    """
    format_in_place(target)

    violations: list[str] = []

    check = _run(["ruff", "check"], target)
    if check.returncode != 0:
        violations.append("ruff check:\n" + (check.stdout or check.stderr).strip())

    typecheck = _run(["mypy"], target)
    if typecheck.returncode != 0:
        violations.append("mypy:\n" + (typecheck.stdout or typecheck.stderr).strip())

    if violations and strict:
        raise LintGateError(
            "Lint gate failed (generated code is dirty — likely a generator bug):\n\n"
            + "\n\n".join(violations)
        )
    return violations
