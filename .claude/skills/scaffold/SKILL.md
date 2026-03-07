---
name: scaffold
description: Generate a new project setup with CLAUDE.md, agent templates, pipeline skill, rules, and hooks from the universal templates. Use when starting a new project.
user-invocable: true
---

# Project Scaffold

Generate a complete Claude Code project setup for a new project.

## Required Input
The user must provide (via $ARGUMENTS or follow-up):
1. **Project name** — short identifier
2. **Project description** — one paragraph
3. **Tech stack** — language, frameworks, key deps
4. **Milestones** — 3-5 high-level milestones
5. **Domain constraints** — project-specific hard facts (optional)

## Steps

1. **Collect input** — if any required field is missing, ask for it.

2. **Generate project CLAUDE.md** from template:
   - Read `templates/CLAUDE.template.md` for the base structure
   - Fill in project-specific sections (description, tech stack, structure, milestones)
   - Domain constraints and project-specific safety rules
   - Keep under 80 lines

3. **Copy universal agent templates:**
   - `.claude/agents/architect.md` — copy from this project's template
   - `.claude/agents/engineer.md` — copy from this project's template
   - `.claude/agents/qa.md` — copy from this project's template

4. **Copy pipeline skill:**
   - `.claude/skills/pipeline/SKILL.md` — copy from this project

5. **Create agent memory files:**
   - `.claude/agents/memory/architect-lessons.md`
   - `.claude/agents/memory/engineer-lessons.md`
   - `.claude/agents/memory/qa-lessons.md`

6. **Create project hooks** in `.claude/settings.json`

7. **Create path-scoped rules** if the project has distinct source areas (e.g., `src/`, `tests/`, `configs/`)

8. **Initialize git** if not already a repo.

9. **Report** — list all files created, remind user to review CLAUDE.md.
