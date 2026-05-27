#!/usr/bin/env bash
# scripts/60-check-public.sh

set -euo pipefail

TASK_DIR="${1:-tasks/task-001}"
REVIEW_NO="001"
EXTRA_INSTRUCTION=""

if [[ $# -ge 2 ]]; then
  if [[ "$2" =~ ^[0-9]+$ ]]; then
    REVIEW_NO="$2"
    EXTRA_INSTRUCTION="${3:-}"
  else
    EXTRA_INSTRUCTION="$2"
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

if [[ ! -d "$REPO_ROOT/public" ]]; then
  echo "public directory not found" >&2
  exit 1
fi

OUTPUT_FILE="$REPO_ROOT/$TASK_DIR/public-check${REVIEW_NO}.md"

mkdir -p "$REPO_ROOT/$TASK_DIR"

"$SCRIPT_DIR/codex-run.sh" \
  read-only \
  prompts/60-check-public-from-change-plan.md \
  "$TASK_DIR" \
  "$REVIEW_NO" \
  "$EXTRA_INSTRUCTION" \
  > "$OUTPUT_FILE"

"$SCRIPT_DIR/check-judgement.sh" "$OUTPUT_FILE" > /dev/null
