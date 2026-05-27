#!/usr/bin/env bash
# scripts/31-apply-test-code-review.sh

set -euo pipefail

TASK_DIR="${1:-tasks/task-001}"
REVIEW_NO="${2:-001}"
EXTRA_INSTRUCTION="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/$TASK_DIR/test-cases.md" ]]; then
  echo "test-cases.md not found: $TASK_DIR/test-cases.md" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/$TASK_DIR/test-code-review${REVIEW_NO}.md" ]]; then
  echo "Test code review file not found: $TASK_DIR/test-code-review${REVIEW_NO}.md" >&2
  exit 1
fi

"$SCRIPT_DIR/codex-run.sh" \
  workspace-write \
  prompts/31-apply-test-code-review.md \
  "$TASK_DIR" \
  "$REVIEW_NO" \
  "$EXTRA_INSTRUCTION"
