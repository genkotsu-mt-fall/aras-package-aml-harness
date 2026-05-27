#!/usr/bin/env bash
# scripts/check-judgement.sh

set -euo pipefail

FILE="${1:-}"

if [[ -z "$FILE" ]]; then
  echo "Usage: scripts/check-judgement.sh <markdown-file>" >&2
  exit 2
fi

if [[ ! -f "$FILE" ]]; then
  echo "judgement file not found: $FILE" >&2
  exit 1
fi

JUDGEMENT="$(awk '
  /^## 判定[[:space:]]*$/ { in_judgement=1; next }
  in_judgement && NF > 0 {
    print
    exit
  }
' "$FILE")"

case "$JUDGEMENT" in
  OK|"修正が必要")
    printf "%s\n" "$JUDGEMENT"
    ;;
  *)
    echo "Unable to read judgement from: $FILE" >&2
    echo "Expected the first non-empty line after '## 判定' to be 'OK' or '修正が必要'." >&2
    echo "Actual: ${JUDGEMENT:-<empty>}" >&2
    exit 1
    ;;
esac
