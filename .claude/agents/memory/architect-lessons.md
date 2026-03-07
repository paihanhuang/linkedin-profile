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

## 2026-03-07 — Template System Design (M3)
- **Action:** Designed manifest-driven template system: manifest.json registry, template engine with conditional blocks, scaffold refactor from hardcoded to data-driven.
- **Outcome:** Design approved after cross-critique identified 10 refinements. All 16 ACs pass.
- **Lesson:** When extracting hardcoded content into templates, distinguish computed content (structure tree from project_name) from static content (hook scripts). Only static content belongs in template files. Also, conditional blocks must be evaluated BEFORE placeholder substitution — otherwise the condition value is already replaced.

## 2026-03-07 — Docs & Validation Design (M4)
- **Action:** Designed architecture docs, token analysis, and cross-project validation tests.
- **Outcome:** Straightforward docs + tests milestone. No blockers from critique.
- **Lesson:** For docs-only milestones, a lighter critique phase is sufficient. Token estimates should be derived from measured file sizes (wc -c), not guessed. Parameterized pytest fixtures are ideal for cross-project testing.
