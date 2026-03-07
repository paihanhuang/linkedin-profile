#!/usr/bin/env bash
# UserPromptSubmit hook: Check if a request looks non-trivial and inject
# a Clarity Gate reminder before Claude processes it.
# This makes the Clarity Gate more deterministic — Claude sees the reminder
# alongside the user's prompt.

set -euo pipefail

INPUT=$(cat)
USER_PROMPT=$(echo "$INPUT" | jq -r '.user_prompt // empty')

if [ -z "$USER_PROMPT" ]; then
  exit 0
fi

# Short prompts (<30 chars) are likely trivial — skip
PROMPT_LEN=${#USER_PROMPT}
if [ "$PROMPT_LEN" -lt 30 ]; then
  exit 0
fi

# Check for indicators of non-trivial work
if echo "$USER_PROMPT" | grep -qiE "(add|build|create|implement|design|refactor|migrate|new feature|new tool|integrate|set up|architecture)"; then
  cat <<'EOF'
CLARITY GATE REMINDER: This request appears non-trivial. Before proceeding:
1. Is anything ambiguous? Ask 1-3 clarifying questions.
2. State key assumptions explicitly.
3. Consider invoking /pipeline for design review.
EOF
fi

exit 0
