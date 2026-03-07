#!/usr/bin/env bash
# SessionStart hook: Inject project state at the start of every session.
# Gives Claude immediate awareness of where things stand — no re-discovery needed.

set -euo pipefail

PROJECT_DIR="/home/etem/Projects/claude-mcp"

echo "=== SESSION STANDUP ==="

# Current milestone from CLAUDE.md
MILESTONE=$(grep -E '^\- \*\*M[0-9]' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | head -5)
if [ -n "$MILESTONE" ]; then
  echo ""
  echo "MILESTONES:"
  echo "$MILESTONE"
fi

# Recent git activity (if git repo)
if [ -d "$PROJECT_DIR/.git" ]; then
  RECENT=$(git -C "$PROJECT_DIR" log --oneline -5 2>/dev/null)
  if [ -n "$RECENT" ]; then
    echo ""
    echo "RECENT COMMITS:"
    echo "$RECENT"
  fi

  # Uncommitted changes
  DIRTY=$(git -C "$PROJECT_DIR" status --short 2>/dev/null)
  if [ -n "$DIRTY" ]; then
    echo ""
    echo "UNCOMMITTED CHANGES:"
    echo "$DIRTY"
  fi
fi

# Open action items from agent memory (last entries)
for AGENT in architect engineer qa; do
  MEMFILE="$PROJECT_DIR/.claude/agents/memory/${AGENT}-lessons.md"
  if [ -f "$MEMFILE" ]; then
    LAST_ENTRY=$(grep -A3 "^## " "$MEMFILE" 2>/dev/null | tail -4)
    if [ -n "$LAST_ENTRY" ] && ! echo "$LAST_ENTRY" | grep -q "^<!-- "; then
      echo ""
      echo "LAST ${AGENT^^} LESSON:"
      echo "$LAST_ENTRY"
    fi
  fi
done

echo ""
echo "=== END STANDUP ==="
