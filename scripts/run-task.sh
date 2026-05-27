#!/usr/bin/env bash
# scripts/run-task.sh

set -euo pipefail

TASK_DIR="${1:-}"
EXTRA_INSTRUCTION="${2:-}"
MAX_REVIEW_LOOPS="${MAX_REVIEW_LOOPS:-3}"
MAX_TASK_CHAIN="${MAX_TASK_CHAIN:-3}"
TASK_CHAIN_INDEX="${TASK_CHAIN_INDEX:-1}"

if [[ -z "$TASK_DIR" ]]; then
  echo "Usage: scripts/run-task.sh <task-dir> [extra-instruction]" >&2
  echo "Example: scripts/run-task.sh tasks/task-004" >&2
  echo "Example: MAX_REVIEW_LOOPS=5 scripts/run-task.sh tasks/task-004" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

review_no() {
  printf "%03d" "$1"
}

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

read_judgement() {
  local file="$1"
  "$SCRIPT_DIR/check-judgement.sh" "$file"
}

require_ok_or_needs_fix() {
  local file="$1"
  read_judgement "$file"
}

echo "Task dir         : $TASK_DIR"
echo "Max review loops : $MAX_REVIEW_LOOPS"
echo "Task chain       : $TASK_CHAIN_INDEX / $MAX_TASK_CHAIN"
echo ""

if [[ ! -f "$REPO_ROOT/$TASK_DIR/change-plan.md" ]]; then
  echo "change-plan.md not found: $TASK_DIR/change-plan.md" >&2
  exit 1
fi

echo "== 05 align change-plan with public =="
"$SCRIPT_DIR/05-align-change-plan-with-public.sh" "$TASK_DIR" "$EXTRA_INSTRUCTION"

echo "== 10 create test-cases =="
"$SCRIPT_DIR/10-create-test-cases.sh" "$TASK_DIR" "$EXTRA_INSTRUCTION"

echo "== 11/12 review and apply test-cases =="
for i in $(seq 1 "$MAX_REVIEW_LOOPS"); do
  no="$(review_no "$i")"
  review_file="$REPO_ROOT/$TASK_DIR/test-cases-review${no}.md"

  "$SCRIPT_DIR/11-review-test-cases.sh" "$TASK_DIR" "$no" "$EXTRA_INSTRUCTION"
  judgement="$(require_ok_or_needs_fix "$review_file")"
  echo "test-cases review ${no}: $judgement"

  if [[ "$judgement" == "OK" ]]; then
    break
  fi

  if [[ "$i" -eq "$MAX_REVIEW_LOOPS" ]]; then
    echo "Reached max test-cases review loops: $MAX_REVIEW_LOOPS" >&2
    exit 1
  fi

  "$SCRIPT_DIR/12-apply-test-cases-review.sh" "$TASK_DIR" "$no" "$EXTRA_INSTRUCTION"
done

echo "== 20 implement tests =="
"$SCRIPT_DIR/20-implement-tests.sh" "$TASK_DIR" "$EXTRA_INSTRUCTION"

echo "== 30/31 review and apply test code =="
for i in $(seq 1 "$MAX_REVIEW_LOOPS"); do
  no="$(review_no "$i")"
  review_file="$REPO_ROOT/$TASK_DIR/test-code-review${no}.md"

  "$SCRIPT_DIR/30-review-tests.sh" "$TASK_DIR" "$no" "$EXTRA_INSTRUCTION"
  judgement="$(require_ok_or_needs_fix "$review_file")"
  echo "test-code review ${no}: $judgement"

  if [[ "$judgement" == "OK" ]]; then
    break
  fi

  if [[ "$i" -eq "$MAX_REVIEW_LOOPS" ]]; then
    echo "Reached max test-code review loops: $MAX_REVIEW_LOOPS" >&2
    exit 1
  fi

  "$SCRIPT_DIR/31-apply-test-code-review.sh" "$TASK_DIR" "$no" "$EXTRA_INSTRUCTION"
done

echo "== 50 implement app =="
"$SCRIPT_DIR/50-implement-app.sh" "$TASK_DIR" "$EXTRA_INSTRUCTION"

echo "== 60 check public =="
"$SCRIPT_DIR/60-check-public.sh" "$TASK_DIR" 001 "$EXTRA_INSTRUCTION"
public_check_file="$REPO_ROOT/$TASK_DIR/public-check001.md"
public_judgement="$(require_ok_or_needs_fix "$public_check_file")"
echo "public check 001: $public_judgement"

if [[ "$public_judgement" != "OK" ]]; then
  if [[ "$TASK_CHAIN_INDEX" -ge "$MAX_TASK_CHAIN" ]]; then
    echo "Public check requires a follow-up task, but reached max task chain: $MAX_TASK_CHAIN" >&2
    echo "Promote it manually with:" >&2
    echo "  scripts/70-promote-public-check.sh $TASK_DIR 001" >&2
    exit 1
  fi

  next_task="$(next_task_dir)"
  echo "Public check requires a follow-up task." >&2
  echo "Promoting to: $next_task" >&2
  "$SCRIPT_DIR/70-promote-public-check.sh" "$TASK_DIR" 001 "$next_task" "$EXTRA_INSTRUCTION"

  echo "Starting next task: $next_task" >&2
  TASK_CHAIN_INDEX="$((TASK_CHAIN_INDEX + 1))" \
    MAX_TASK_CHAIN="$MAX_TASK_CHAIN" \
    MAX_REVIEW_LOOPS="$MAX_REVIEW_LOOPS" \
    "$SCRIPT_DIR/run-task.sh" "$next_task" "$EXTRA_INSTRUCTION"
  exit $?
fi

echo "== 90 harness =="
"$SCRIPT_DIR/90-harness.sh"

echo ""
echo "Task completed: $TASK_DIR"
