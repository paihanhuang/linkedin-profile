---
paths:
  - ".claude/skills/**"
  - "skills/**"
---

# Skill Conventions

- Every skill must have YAML frontmatter with: name, description, user-invocable
- Skill names are lowercase with hyphens only
- Description must be specific enough for Claude to auto-invoke when relevant
- Use `$ARGUMENTS` for user input, `$0`/`$1`/`$2` for positional args
- Keep SKILL.md under 500 lines — use reference files for detailed content
- Skills that have side effects (deploy, send, push) must set `disable-model-invocation: true`
- Test skills by invoking them manually before relying on auto-invocation
