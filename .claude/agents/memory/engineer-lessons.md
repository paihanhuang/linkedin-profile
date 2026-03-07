# Engineer Lessons

<!-- Append entries after each pipeline run. Format:
## [Date] — [Task Summary]
- **Action:** What was implemented
- **Outcome:** What happened
- **Lesson:** What to remember next time
-->

## 2026-03-07 — MCP Server Initial Build (M2)
- **Action:** Built FastMCP server with 6 tools across 3 modules (patterns, scaffold, checklist) plus templates directory
- **Outcome:** All 36 acceptance criteria pass. Server starts, all tools registered with descriptions.
- **Lesson:** When using `asyncio.create_subprocess_shell` with timeout, must use `start_new_session=True` and `os.killpg` to kill the entire process group — `proc.kill()` alone only kills the shell parent, leaving child processes (e.g., `sleep`) running and causing hangs. Also, hatchling requires explicit `[tool.hatch.build.targets.wheel] packages = ["src"]` when the package directory name doesn't match the project name.

## 2026-03-07 — Template System Implementation (M3)
- **Action:** Refactored scaffold.py from hardcoded strings to manifest-driven template processing. Created template_engine.py with conditional blocks and validation. 31 pytest tests.
- **Outcome:** 31/31 tests pass. All 16 ACs verified by QA.
- **Lesson:** System PYTHONPATH with ROS packages leaks into venvs and breaks pytest plugin loading. Use `PYTHONPATH=""` when running tests. Also, template doc comments using the same `{{PLACEHOLDER}}` syntax as the engine will get rendered — strip them or use a different comment syntax.
