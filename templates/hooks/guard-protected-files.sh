#!/usr/bin/env bash
# Guard protected files from accidental edits.
# Customize the PROTECTED_PATTERNS array for your project.
PROTECTED_PATTERNS=(
  ".claude/agents/*.md"
  ".claude/skills/*/SKILL.md"
)
exit 0
