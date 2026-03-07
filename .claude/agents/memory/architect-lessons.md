# Architect Lessons

<!-- Append entries after each pipeline run. Format:
## [Date] — [Task Summary]
- **Action:** What was designed
- **Outcome:** What happened
- **Lesson:** What to remember next time
-->

## 2026-03-07 — MCP Server Design (M2)
- **Action:** Designed FastMCP server architecture with 6 tools across 3 modules (patterns CRUD, scaffold, checklist), atomic JSON store, single-pass template replacement, and async subprocess execution with process group cleanup.
- **Outcome:** Design approved after cross-critique. Engineer implemented successfully, QA found 2 issues (exit 126/127 mapping, search OR vs AND) — both fixed and verified.
- **Lesson:** Spec ambiguity ("name/description" matching) must be resolved explicitly in the design doc — don't leave it for implementation to guess. Also, shell exit codes (126=permission denied, 127=command not found) need special handling in acceptance criteria — distinguish from normal non-zero exits.
