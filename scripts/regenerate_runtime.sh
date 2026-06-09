#!/usr/bin/env bash
#
# Regenerate the in-repo runtime (src/sema/runtime) and lint it in one step.
#
# The generator already sorts its output (imports, topo_sort), so `ruff format`
# is the last source of churn: running it here makes a *second* regen produce a
# zero diff. `ruff check` + `mypy` run as gates that surface generator bugs
# (dirty generated code). They are reported by default and become fatal only
# with `--strict`, because the generator currently emits a small set of known
# violations that are a tracked cleanup (see wiki/sema/changelog.md). `ruff
# format` always runs.
#
# Usage:
#   scripts/regenerate_runtime.sh            # regenerate, format, report lint
#   scripts/regenerate_runtime.sh --strict   # fail if ruff check / mypy is dirty
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

echo "==> ruff format (in place)"
uv run ruff format "${RUNTIME_DIR}"

status=0

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
  echo "WARNING: generated runtime has lint findings (reported above; see the" >&2
  echo "         tracked generator-cleanup follow-up). Re-run with --strict to" >&2
  echo "         make these fatal." >&2
fi

echo "==> Done."
