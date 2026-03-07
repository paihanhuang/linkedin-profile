# QA Lessons

<!-- Append entries after each pipeline run. Format:
## [Date] — [Task Summary]
- **Action:** What was verified
- **Outcome:** What was found
- **Lesson:** What to check next time
-->

## 2026-03-07 — FastMCP Server Initial Verification

- **Action:** Verified all 36 acceptance criteria across pattern tools, scaffold, checklist, and server integration.
- **Outcome:** 35/36 PASS. AC-C9 (command not found → status "error") returns "fail" instead because shell exit code 127 is non-zero. AC-P9 query matching uses AND (both name AND description must match), which may differ from the AC's "name/description" wording if OR was intended.
- **Lesson:** When testing shell commands via asyncio subprocess, "command not found" is a shell-level error (exit 127), not a Python exception — so it produces "fail" not "error". Test with actual shell commands, not just reasoning about the code. Also, verify ambiguous spec wording ("name/description" could mean AND or OR) by testing edge cases explicitly.

## 2026-03-07 — M3 Template System Verification

- **Action:** Verified 16 acceptance criteria for the manifest-driven template system: template extraction, conditional blocks, manifest validation, force/no-force overwrite, error returns, and full scaffold for ML and web project types.
- **Outcome:** All 16 ACs PASS, all 31 tests pass. One cosmetic note: the HTML comment header in CLAUDE.template.md (lines 3-10) lists placeholder names using `{{PLACEHOLDER}}` syntax, which gets substituted during rendering, producing a garbled comment in the output. Not a functional issue. Also, memory-header.template.md lacks the header comment listing placeholders required by `.claude/rules/templates.md`.
- **Lesson:** When templates contain documentation comments using the same placeholder syntax as the engine, those comments will be rendered too. Either strip doc comments before rendering, use a different syntax for doc comments (e.g., `{# ... #}`), or remove them from the output template. Also test edge cases like `domain_constraints=[]` (empty list vs None) — both should produce the same "omit" behavior.
