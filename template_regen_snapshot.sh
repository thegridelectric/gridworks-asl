#!/usr/bin/env bash
#
# template_regen_snapshot.sh — copy into a consumer repo as
# scripts/regen_sema_snapshot.sh and fill in the three CHANGEME facts.
# Companion to template_seed_request.yaml (the seed it consumes).
#
# SCOPE: this regenerates a CONSUMER repo's vendored snapshot (src/<pkg>/sema)
# via `sema snapshot prepare|build`. It does NOT touch sema's own runtime:
# after editing definitions/, regenerate src/sema/runtime/ (what
# `sema validate` and the codec load) with scripts/regenerate_runtime.py.
# The two regens are parallel mechanisms; neither invokes the other.
#
# Regenerates the repo's vendored Sema snapshot from the canonical sema
# repo. The vendored tree is GENERATED — never hand-edit it; edit the seed
# (or the sema definitions) and re-run.
#
# The build mechanics are the sema CLI's (`sema snapshot --help` is the
# source of truth). The CLI refuses to run from a dirty sema checkout and
# writes only under <sema>/output, so the snapshot is reproducible from
# the sema commit the checkout sits on — check out the ref you intend to
# ship from before running.
#
# Usage:
#   scripts/regen_sema_snapshot.sh                 # sibling ../sema checkout
#   SEMA_REPO=/path/to/sema scripts/regen_sema_snapshot.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEMA_REPO="${SEMA_REPO:-$(cd "${REPO_ROOT}/../sema" 2>/dev/null && pwd || true)}"

# The three repo-specific facts (gjk's values shown as a worked example):
PACKAGE_NAME="CHANGEME"                                  # e.g. gjk — build derives import_root = <name>.sema; do NOT pass "<name>.sema"
SEED="${REPO_ROOT}/src/CHANGEME/sema_seed_request.yaml"  # e.g. src/gjk/sema_seed_request.yaml
VENDOR_DIR="${REPO_ROOT}/src/CHANGEME/sema"              # e.g. src/gjk/sema — the mirrored generated tree

if [[ "${PACKAGE_NAME}" == "CHANGEME" ]]; then
  echo "error: edit the three CHANGEME facts first (package name, seed, vendor dir)." >&2
  exit 1
fi

if [[ -z "${SEMA_REPO}" || ! -d "${SEMA_REPO}" ]]; then
  echo "error: sema repo not found." >&2
  echo "       set SEMA_REPO=/path/to/sema and re-run (default looked for a" >&2
  echo "       sibling checkout at ${REPO_ROOT}/../sema)." >&2
  exit 1
fi

echo "==> sema repo: ${SEMA_REPO} @ $(git -C "${SEMA_REPO}" rev-parse --short HEAD)"
echo "==> seed:      ${SEED}"
echo "==> package:   ${PACKAGE_NAME}"

cd "${SEMA_REPO}"
echo "==> sema snapshot prepare"
uv run sema snapshot prepare "${SEED}"
echo "==> sema snapshot build --package-name ${PACKAGE_NAME}"
uv run sema snapshot build --package-name "${PACKAGE_NAME}"

echo "==> mirror ${SEMA_REPO}/output/sema -> ${VENDOR_DIR}"
rsync -a --delete --exclude='__pycache__' \
  "${SEMA_REPO}/output/sema/" "${VENDOR_DIR}/"

echo "==> done. review the diff (git status) and run your repo's tests."
