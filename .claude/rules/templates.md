---
paths:
  - "templates/**"
---

# Template Conventions

- Use `{{PLACEHOLDER}}` syntax for all replaceable values
- Placeholder names must be UPPER_SNAKE_CASE
- Every template must include a header comment listing all placeholders and their descriptions
- Templates must produce valid output when all placeholders are filled — no broken markdown
- Keep templates minimal — only include sections that vary per project
- Common/universal content (agent templates, skills) should be copied, not templated
- Test templates by generating at least 2 different project types (ML, web app)
