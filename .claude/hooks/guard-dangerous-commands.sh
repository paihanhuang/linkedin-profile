#!/usr/bin/env bash
# PreToolUse hook for Bash: Block dangerous commands deterministically.
# Exit 0 = allow, Exit 2 = block (stderr shown to Claude as feedback).

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Dangerous patterns to block
BLOCKED_PATTERNS=(
  "rm -rf /"
  "rm -rf ~"
  "rm -rf \."
  "git push --force"
  "git push -f"
  "git reset --hard"
  "git clean -fd"
  "git checkout -- ."
  "git restore ."
  "drop table"
  "DROP TABLE"
  "truncate table"
  "TRUNCATE TABLE"
  "> /dev/sda"
  "mkfs\."
  "dd if="
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qF "$pattern" 2>/dev/null || echo "$COMMAND" | grep -q "$pattern" 2>/dev/null; then
    echo "BLOCKED: Dangerous command detected: '$pattern'. Ask Traso for explicit approval before running destructive operations." >&2
    exit 2
  fi
done

exit 0
