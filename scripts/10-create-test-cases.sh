#!/usr/bin/env bash
# scripts/10-create-test-cases.sh

set -euo pipefail

TASK_DIR="${1:-tasks/task-001}"
EXTRA_INSTRUCTION="${2:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

"$SCRIPT_DIR/codex-run.sh" \
  workspace-write \
  prompts/10-create-test-cases.md \
  "$TASK_DIR" \
  001 \
  "$EXTRA_INSTRUCTION"
