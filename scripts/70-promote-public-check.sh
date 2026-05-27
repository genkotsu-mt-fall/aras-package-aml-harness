#!/usr/bin/env bash
# scripts/70-promote-public-check.sh

set -euo pipefail

SOURCE_TASK_DIR="${1:-tasks/task-001}"
CHECK_NO="${2:-001}"
TARGET_TASK_DIR="${3:-}"
EXTRA_INSTRUCTION="${4:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

next_task_dir() {
  local max=0
  local dir
  local name
  local num

  shopt -s nullglob
  for dir in "$REPO_ROOT"/tasks/task-[0-9][0-9][0-9]; do
    name="$(basename "$dir")"
    num="${name#task-}"
    if [[ "$num" =~ ^[0-9]+$ && "$((10#$num))" -gt "$max" ]]; then
      max="$((10#$num))"
    fi
  done
  shopt -u nullglob

  printf "tasks/task-%03d" "$((max + 1))"
}

if [[ -n "$TARGET_TASK_DIR" && -z "$EXTRA_INSTRUCTION" && ! "$TARGET_TASK_DIR" =~ ^tasks/task-[0-9][0-9][0-9]$ ]]; then
  EXTRA_INSTRUCTION="$TARGET_TASK_DIR"
  TARGET_TASK_DIR=""
fi

if [[ -z "$TARGET_TASK_DIR" ]]; then
  TARGET_TASK_DIR="$(next_task_dir)"
fi

SOURCE_CHECK="$SOURCE_TASK_DIR/public-check${CHECK_NO}.md"
TARGET_CHANGE_PLAN="$TARGET_TASK_DIR/change-plan.md"

if [[ ! -f "$REPO_ROOT/$SOURCE_CHECK" ]]; then
  echo "public-check file not found: $SOURCE_CHECK" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/$SOURCE_TASK_DIR/change-plan.md" ]]; then
  echo "source change-plan.md not found: $SOURCE_TASK_DIR/change-plan.md" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/$TARGET_TASK_DIR"

if [[ -f "$REPO_ROOT/$TARGET_CHANGE_PLAN" ]]; then
  echo "target change-plan.md already exists: $TARGET_CHANGE_PLAN" >&2
  exit 1
fi

PROMOTE_INSTRUCTION="入力 public-check: ${SOURCE_CHECK}
入力元 change-plan: ${SOURCE_TASK_DIR}/change-plan.md
入力元 test-cases: ${SOURCE_TASK_DIR}/test-cases.md
出力 change-plan: ${TARGET_CHANGE_PLAN}"

if [[ -n "$EXTRA_INSTRUCTION" ]]; then
  PROMOTE_INSTRUCTION="${PROMOTE_INSTRUCTION}

追加の指示:
${EXTRA_INSTRUCTION}"
fi

"$SCRIPT_DIR/codex-run.sh" \
  workspace-write \
  prompts/70-promote-public-check-to-change-plan.md \
  "$TARGET_TASK_DIR" \
  "$CHECK_NO" \
  "$PROMOTE_INSTRUCTION"

echo "Promoted public check to: $TARGET_CHANGE_PLAN" >&2
