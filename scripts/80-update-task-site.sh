#!/usr/bin/env bash
# scripts/80-update-task-site.sh

set -euo pipefail

EXTRA_INSTRUCTION="${1:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/docs/task-site/data"

mkdir -p "$DATA_DIR"

needs_update() {
  local task_dir="$1"
  local output_file="$2"
  local source

  if [[ ! -f "$output_file" ]]; then
    return 0
  fi

  shopt -s nullglob
  for source in "$task_dir"/*.md; do
    if [[ "$source" -nt "$output_file" ]]; then
      shopt -u nullglob
      return 0
    fi
  done
  shopt -u nullglob

  return 1
}

changed=0

shopt -s nullglob
for task_dir in "$REPO_ROOT"/tasks/task-[0-9][0-9][0-9]; do
  task_name="$(basename "$task_dir")"
  output_file="$DATA_DIR/$task_name.json"

  if needs_update "$task_dir" "$output_file"; then
    echo "== summarize $task_name =="
    "$SCRIPT_DIR/80-summarize-task-site.sh" "tasks/$task_name" "$EXTRA_INSTRUCTION"
    changed=$((changed + 1))
  else
    echo "skip $task_name: summary is up to date"
  fi
done
shopt -u nullglob

"$SCRIPT_DIR/81-build-task-site-manifest.sh"

echo "Task summaries updated: $changed"
