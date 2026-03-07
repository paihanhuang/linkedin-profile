#!/usr/bin/env bash
# PreToolUse hook: Block direct edits to agent templates and memory files without confirmation.
# Exit 0 = allow, Exit 2 = block (stderr shown to Claude as feedback).

set -euo pipefail

# Read the file_path from the tool input JSON on stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Protected patterns: agent templates and pipeline skill
PROTECTED_PATTERNS=(
  ".claude/agents/architect.md"
  ".claude/agents/engineer.md"
  ".claude/agents/qa.md"
  ".claude/skills/pipeline/SKILL.md"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern" ]]; then
    echo "BLOCKED: $FILE_PATH is a protected template. Ask Traso before modifying universal templates." >&2
    exit 2
  fi
done

exit 0
