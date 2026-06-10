#!/usr/bin/env bash
#
# Regenerate the in-repo runtime (src/sema/runtime) and report hygiene.
#
# CANONICAL OUTPUT == ruff-formatted generator output. `regenerate_runtime.py`
# runs `ruff format` as its final pass (via generate_runtime_from_dag), so the
# committed runtime is ruff-clean and the `test_runtime_generation_*` drift
# guards compare against formatted output. ruff is the single source of style —
# the templates need not match it exactly.
#
# So `ruff format` / `ruff check` / `mypy` all run as REPORTS here, never in
# place: the `.py` already formatted the tree, so `ruff format --check` should
# pass clean; `ruff check` + `mypy` surface the remaining known generator
# hygiene findings (over-/under-tracked typing imports; pydantic/enum dynamics
# mypy can't follow) without mutating anything. Findings are reported by default
# and become fatal only with `--strict`.
#
# (History: this script once ran `ruff format` *in place*, which diverged from a
# then-raw committed runtime and broke the drift guards. The fix landed in two
# steps: first make this wrapper report-only; then make the generator format at
# the source — done — so canonical and `--check` now agree.)
#
# Usage:
#   scripts/regenerate_runtime.sh            # regenerate, report hygiene
#   scripts/regenerate_runtime.sh --strict   # fail if format / check / mypy dirty
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
fi

RUNTIME_DIR="src/sema/runtime"

echo "==> Regenerating ${RUNTIME_DIR}"
uv run python scripts/regenerate_runtime.py

status=0

echo "==> ruff format --check (report only; does NOT modify the runtime)"
if ! uv run ruff format --check "${RUNTIME_DIR}"; then
  status=1
fi

echo "==> ruff check"
if ! uv run ruff check "${RUNTIME_DIR}"; then
  status=1
fi

echo "==> mypy"
if ! uv run mypy "${RUNTIME_DIR}"; then
  status=1
fi

if [[ "${status}" -ne 0 ]]; then
  if [[ "${STRICT}" -eq 1 ]]; then
    echo "ERROR: generated runtime is lint-dirty (--strict)." >&2
    exit 1
  fi
  echo "WARNING: generated runtime has hygiene findings (format/lint/type," >&2
  echo "         reported above; see the tracked generator-cleanup follow-up)." >&2
  echo "         The runtime was NOT modified. Re-run with --strict to make" >&2
  echo "         these fatal." >&2
fi

echo "==> Done."
