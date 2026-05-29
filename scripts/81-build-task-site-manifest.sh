#!/usr/bin/env bash
# scripts/81-build-task-site-manifest.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/docs/task-site/data"
MANIFEST_FILE="$DATA_DIR/manifest.json"

mkdir -p "$DATA_DIR"

{
  printf '{\n'
  printf '  "tasks": [\n'

  first=1
  shopt -s nullglob
  for file in "$DATA_DIR"/task-[0-9][0-9][0-9].json; do
    name="$(basename "$file")"
    task_id="${name%.json}"
    if [[ "$first" -eq 0 ]]; then
      printf ',\n'
    fi
    first=0
    printf '    {"id":"%s","file":"data/%s"}' "$task_id" "$name"
  done
  shopt -u nullglob

  printf '\n'
  printf '  ]\n'
  printf '}\n'
} > "$MANIFEST_FILE"

echo "Updated: docs/task-site/data/manifest.json"
