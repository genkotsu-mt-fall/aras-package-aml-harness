#!/usr/bin/env bash
# scripts/codex-run.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

usage() {
  cat <<'EOF'
Usage:
  scripts/codex-run.sh <sandbox> <prompt-file> [task-dir] [review-no] [extra-instruction]

Examples:
  scripts/codex-run.sh read-only prompts/11-review-test-cases.md tasks/task-001 001
  scripts/codex-run.sh workspace-write prompts/10-create-test-cases.md tasks/task-001
  scripts/codex-run.sh workspace-write prompts/10-create-test-cases.md tasks/task-001 001 "AML例は短くする"
EOF
}

if [[ $# -lt 2 || $# -gt 5 ]]; then
  usage
  exit 2
fi

SANDBOX="$1"
PROMPT_FILE="$2"
TASK_DIR="${3:-tasks/task-001}"
REVIEW_NO="${4:-001}"
EXTRA_INSTRUCTION="${5:-}"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Prompt file not found: $PROMPT_FILE" >&2
  exit 1
fi

case "$SANDBOX" in
  read-only|workspace-write)
    ;;
  *)
    echo "Invalid sandbox: $SANDBOX" >&2
    echo "Allowed: read-only, workspace-write" >&2
    exit 1
    ;;
esac

TEMP_PROMPT="$(mktemp "${TMPDIR:-/tmp}/codex-prompt.XXXXXX")"
trap 'rm -f "$TEMP_PROMPT"' EXIT

LOG_DIR="$REPO_ROOT/runs/codex-exec"
mkdir -p "$LOG_DIR"
TASK_NAME="$(basename "$TASK_DIR")"
LOG_FILE="$LOG_DIR/${TASK_NAME}-review${REVIEW_NO}-$(date +%Y%m%d-%H%M%S).log"

cat > "$TEMP_PROMPT" <<EOF
対象タスクディレクトリは ${TASK_DIR} です。
レビュー番号は ${REVIEW_NO} です。

この実行では、以下のパスを使ってください。

- 変更プラン: ${TASK_DIR}/change-plan.md
- テストケース: ${TASK_DIR}/test-cases.md
- レビュー結果: ${TASK_DIR}/test-cases-review${REVIEW_NO}.md

EOF

if [[ -n "$EXTRA_INSTRUCTION" ]]; then
  cat >> "$TEMP_PROMPT" <<EOF
## 追加命令

${EXTRA_INSTRUCTION}

EOF
fi

cat "$PROMPT_FILE" >> "$TEMP_PROMPT"

{
  echo "Repository        : $REPO_ROOT"
  echo "Requested sandbox : $SANDBOX"
  echo "Prompt            : $PROMPT_FILE"
  echo "Task dir          : $TASK_DIR"
  echo "Review no         : $REVIEW_NO"
  echo "Extra instruction : $EXTRA_INSTRUCTION"
  echo "Log file          : $LOG_FILE"
  echo ""
} >> "$LOG_FILE"

codex exec \
  --cd . \
  --dangerously-bypass-approvals-and-sandbox \
  - < "$TEMP_PROMPT" \
  2>> "$LOG_FILE"
