#!/usr/bin/env bash
# Stop hook: After Claude finishes responding, check if a pipeline was running
# and remind to update agent memory files if needed.
# Exit 0 = inject reminder into context. Only triggers if pipeline-related keywords found.

set -euo pipefail

INPUT=$(cat)
STOP_REASON=$(echo "$INPUT" | jq -r '.stop_reason // empty')

# Only trigger on end_turn (not tool_use mid-conversation)
if [ "$STOP_REASON" != "end_turn" ]; then
  exit 0
fi

# Check recent assistant message for pipeline indicators
LAST_MSG=$(echo "$INPUT" | jq -r '.assistant_message // empty')

if echo "$LAST_MSG" | grep -qiE "(pipeline|architect artifact|engineer artifact|qa artifact|PASS_CRITERIA|ACTION_ITEMS|LESSONS_LEARNED)"; then
  echo "Reminder: If a pipeline step just completed, update the relevant agent memory file in .claude/agents/memory/."
fi

exit 0
