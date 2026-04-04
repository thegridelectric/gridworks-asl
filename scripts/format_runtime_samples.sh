#!/usr/bin/env bash
set -euo pipefail

find tests/runtime_samples -type f -name '*.json' -print0 |
while IFS= read -r -d '' f; do
  tmp="${f}.pretty"
  python3 -m json.tool "$f" > "$tmp"
  mv "$tmp" "$f"
done
