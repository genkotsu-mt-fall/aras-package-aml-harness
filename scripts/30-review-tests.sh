#!/usr/bin/env bash
# scripts/30-review-tests.sh

set -euo pipefail

TASK_DIR="${1:-tasks/task-001}"
REVIEW_NO="${2:-001}"
EXTRA_INSTRUCTION="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUTPUT_FILE="$REPO_ROOT/$TASK_DIR/test-code-review${REVIEW_NO}.md"

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/$TASK_DIR/test-cases.md" ]]; then
  echo "test-cases.md not found: $TASK_DIR/test-cases.md" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/$TASK_DIR"

"$SCRIPT_DIR/codex-run.sh" \
  read-only \
  prompts/30-review-test-code.md \
  "$TASK_DIR" \
  "$REVIEW_NO" \
  "$EXTRA_INSTRUCTION" \
  > "$OUTPUT_FILE"

"$SCRIPT_DIR/check-judgement.sh" "$OUTPUT_FILE" > /dev/null
