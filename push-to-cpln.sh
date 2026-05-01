#!/usr/bin/env bash
# push-to-cpln.sh — manual deploy to Control Plane from a local machine.
#
# Mirrors .github/workflows/deploy-app.yaml step-for-step but runs entirely
# off your laptop (no `git push` required):
#   1. Apply forward-only migrations to the prod base.
#   2. Build + push the app image to Control Plane.
#   3. Render the workload YAML and apply it (rolls a new version).
#
# Pre-conditions:
#   - cpln CLI installed and `cpln profile login` already done.
#   - psql + jq on PATH.
#   - .secrets/sema-prod-base.json present (admin connection string).
#
# Usage:
#   ./push-to-cpln.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# ─── cpln coordinates ───────────────────────────────────────────────────────
CPLN_ORG="effortlessapi"
CPLN_GVC="gridworks-sema"
CPLN_WORKLOAD="gridworks-sema"
CPLN_IMAGE="gridworks-sema"
CPLN_SECRET_NAME="gridworks-sema"

# ─── prerequisite checks ────────────────────────────────────────────────────
for cmd in cpln psql jq git; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: '$cmd' not found on PATH." >&2
        exit 1
    fi
done

if [[ ! -f .secrets/sema-prod-base.json ]]; then
    echo "ERROR: .secrets/sema-prod-base.json missing — can't migrate prod." >&2
    exit 1
fi

# ─── tag derivation ─────────────────────────────────────────────────────────
# The workflow uses the commit SHA. We do the same when clean; if the tree
# is dirty we still deploy (you said you don't want to commit/push) but mark
# the tag so it's obvious what's running came from an uncommitted state.
SHORT_SHA="$(git rev-parse --short HEAD)"
if [[ -n "$(git status --porcelain)" ]]; then
    SHORT_SHA="${SHORT_SHA}-dirty$(date +%s)"
    echo "WARN: working tree is dirty; tagging image '${SHORT_SHA}'." >&2
fi

# ─── 1. migrate prod base ───────────────────────────────────────────────────
echo ""
echo "→ [1/3] Applying migrations against prod base"
BASE_ADMIN_URL="$(jq -r '.admin.connectionString' .secrets/sema-prod-base.json)"
postgres/migrations/migrate-prod.sh "$BASE_ADMIN_URL"

# ─── 2. build + push image ──────────────────────────────────────────────────
echo ""
echo "→ [2/3] Building + pushing image ${CPLN_IMAGE}:${SHORT_SHA}"
cpln image docker-login --org "$CPLN_ORG"
cpln image build \
    --org "$CPLN_ORG" \
    --name "${CPLN_IMAGE}:${SHORT_SHA}" \
    --dockerfile Dockerfile \
    --push

# ─── 3. render + apply workload ─────────────────────────────────────────────
echo ""
echo "→ [3/3] Rendering + applying workload ${CPLN_WORKLOAD}"
WORKLOAD_RENDERED="$(mktemp -t cpln-workload-XXXXXX.yaml)"
trap 'rm -f "$WORKLOAD_RENDERED"' EXIT
sed \
    -e "s|WORKLOAD_NAME|${CPLN_WORKLOAD}|g" \
    -e "s|IMAGE_NAME_TAG|${CPLN_IMAGE}:${SHORT_SHA}|g" \
    -e "s|ORG_NAME|${CPLN_ORG}|g" \
    -e "s|GVC_NAME|${CPLN_GVC}|g" \
    -e "s|IDENTITY_NAME|${CPLN_WORKLOAD}|g" \
    -e "s|SECRET_NAME|${CPLN_SECRET_NAME}|g" \
    .cpln/cpln-app-workload.yaml > "$WORKLOAD_RENDERED"

cpln apply --org "$CPLN_ORG" --gvc "$CPLN_GVC" -f "$WORKLOAD_RENDERED"

echo ""
echo "✓ Deployed ${CPLN_IMAGE}:${SHORT_SHA} → workload ${CPLN_WORKLOAD}"
echo "  Tail logs: cpln logs --org ${CPLN_ORG} --gvc ${CPLN_GVC} --workload ${CPLN_WORKLOAD}"
