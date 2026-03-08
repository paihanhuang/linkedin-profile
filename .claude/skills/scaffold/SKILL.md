---
name: scaffold
description: Generates a new project with CLAUDE.md, agent templates, pipeline skill, hooks, and rules from universal templates. Invoked when starting a new project or bootstrapping Claude Code for an existing codebase.
user-invocable: true
---

# Project Scaffold

Generate a complete Claude Code project setup using `claude-mcp:scaffold_project`.

## Required Input

Collect from $ARGUMENTS or follow-up:
1. **Project name** — short identifier
2. **Project description** — one paragraph
3. **Tech stack** — language, frameworks, key deps
4. **Milestones** — 3-5 high-level milestones
5. **Domain constraints** — project-specific hard facts (optional)

## Steps

1. **Collect input** — if any required field is missing, ask for it.
2. **Call `claude-mcp:scaffold_project`** with collected parameters.
3. **Review output** — verify all files were created.
4. **Initialize git** if not already a repo.
5. **Report** — list all files created, remind user to review CLAUDE.md.

## Fallback (if MCP server unavailable)

If `claude-mcp:scaffold_project` is not available, create files manually:
- `CLAUDE.md` — render from `templates/CLAUDE.template.md`
- `.claude/agents/{architect,engineer,qa}.md` — copy from templates
- `.claude/agents/memory/{architect,engineer,qa}-lessons.md` — empty with header
- `.claude/skills/pipeline/SKILL.md` — copy from templates
- `.claude/settings.json` — hooks configuration
- `.claude/rules/` — path-scoped rules if project has distinct source areas
