#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

uv run python "${ROOT_DIR}/src/sema/tools/build_dependency_closure.py"
uv run python "${ROOT_DIR}/src/sema/tools/build_lookup.py"
uv run python "${ROOT_DIR}/src/sema/tools/build_reverse_dependencies.py"
uv run python "${ROOT_DIR}/src/sema/tools/build_versions.py"
