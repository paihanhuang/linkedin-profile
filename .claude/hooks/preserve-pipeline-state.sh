#!/usr/bin/env bash
# PreCompact hook: Before context compaction, inject a reminder about pipeline state
# so critical information survives compaction.

set -euo pipefail

cat <<'EOF'
PIPELINE STATE REMINDER: If you were mid-pipeline or in autopilot mode, recall:
- Which step were you on? (Architect → Critique → Synthesize → Engineer → QA)
- What artifacts have been produced and approved?
- What task was being worked on?
Re-read .claude/skills/pipeline/SKILL.md if you need the full protocol.
Check .claude/agents/memory/ for recent lessons.
EOF

# If autopilot progress file exists, inject it as durable state
if [ -f "autopilot-progress.md" ]; then
  echo ""
  echo "AUTOPILOT STATE — resume from this:"
  cat autopilot-progress.md
fi

exit 0
