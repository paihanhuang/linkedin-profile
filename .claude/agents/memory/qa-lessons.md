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
