#!/usr/bin/env bash
#
# Regenerate the in-repo runtime (src/sema/runtime) and report hygiene.
#
# CANONICAL OUTPUT == the raw `scripts/regenerate_runtime.py` output. That is
# what the committed runtime IS and what the `test_runtime_generation_*` drift
# guards compare against. This wrapper MUST NOT mutate the runtime into a
# *different* canonical form, or it silently breaks those guards.
#
# So `ruff format` / `ruff check` / `mypy` all run as REPORTS here, never in
# place: they surface generator hygiene (e.g. an over-long `e.compile(...)` line
# `ruff format` would wrap) as the tracked generator-cleanup signal, but they do
# not touch the files. The generator already sorts its output (imports,
# topo_sort) and is deterministic, so a second `.py` regen is already zero-diff
# without any formatting step. Findings are reported by default and become fatal
# only with `--strict`.
#
# (History: this script used to run `ruff format` in place on the theory that
# the committed runtime was ruff-formatted. It isn't — the drift guards pin it
# to the raw generator output — so the in-place format diverged from canonical
# and broke the build. Making the runtime ruff-clean at the source is the
# tracked generator-cleanup follow-up; until then the format step stays a
# report.)
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
