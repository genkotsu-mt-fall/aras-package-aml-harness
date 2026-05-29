#!/usr/bin/env bash
# scripts/80-summarize-task-site.sh

set -euo pipefail

TASK_DIR="${1:-}"
EXTRA_INSTRUCTION="${2:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -z "$TASK_DIR" ]]; then
  echo "Usage: scripts/80-summarize-task-site.sh <task-dir> [extra-instruction]" >&2
  echo "Example: scripts/80-summarize-task-site.sh tasks/task-010" >&2
  exit 2
fi

if [[ ! -d "$REPO_ROOT/$TASK_DIR" ]]; then
  echo "Task directory not found: $TASK_DIR" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

TASK_NAME="$(basename "$TASK_DIR")"
OUTPUT_DIR="$REPO_ROOT/docs/task-site/data"
OUTPUT_FILE="$OUTPUT_DIR/$TASK_NAME.json"

mkdir -p "$OUTPUT_DIR"

"$SCRIPT_DIR/codex-run.sh" \
  workspace-write \
  prompts/80-summarize-task-site-json.md \
  "$TASK_DIR" \
  001 \
  "$EXTRA_INSTRUCTION"

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Expected summary JSON was not created: docs/task-site/data/$TASK_NAME.json" >&2
  exit 1
fi

echo "Updated: docs/task-site/data/$TASK_NAME.json"
