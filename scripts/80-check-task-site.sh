#!/usr/bin/env bash
# scripts/80-check-task-site.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/docs/task-site/data"

stale=0

shopt -s nullglob
for task_dir in "$REPO_ROOT"/tasks/task-[0-9][0-9][0-9]; do
  task_name="$(basename "$task_dir")"
  output_file="$DATA_DIR/$task_name.json"

  if [[ ! -f "$output_file" ]]; then
    echo "missing $task_name"
    stale=$((stale + 1))
    continue
  fi

  for source in "$task_dir"/*.md; do
    if [[ "$source" -nt "$output_file" ]]; then
      echo "stale $task_name"
      stale=$((stale + 1))
      break
    fi
  done
done
shopt -u nullglob

if [[ "$stale" -eq 0 ]]; then
  echo "task site summaries are up to date"
fi

exit "$stale"
