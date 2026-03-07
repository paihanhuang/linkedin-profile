# CLAUDE.md - Project Operating Contract

## Project

**Claude Code Optimization Toolkit** (`claude-mcp`) — infrastructure for optimizing Claude Code workflows across projects: universal agent templates, MCP server for token efficiency, skills archive, and project scaffolding.

Goals:
1. Improve deliverable quality via cross-critique design pipeline
2. Ensure robustness through universal, project-agnostic templates
3. Build transferable setup (skills, templates, scaffolding)
4. Minimize token waste via MCP tools and deduplication

## Tech Stack

- **Language:** Python 3.11+
- **MCP Framework:** FastMCP
- **Package management:** uv
- **Templates:** Markdown with `{{PLACEHOLDER}}` syntax
- **No heavy external deps** unless justified

## Project Structure

```
claude-mcp/
├── CLAUDE.md                        # Project-specific context
├── .claude/
│   ├── settings.json                # Hooks configuration
│   ├── hooks/                       # Hook scripts
│   │   ├── guard-protected-files.sh # Block edits to universal templates
│   │   ├── memory-reminder.sh       # Post-pipeline memory update reminder
│   │   └── preserve-pipeline-state.sh # Re-inject state before compaction
│   ├── agents/
│   │   ├── architect.md             # Design agent (universal)
│   │   ├── engineer.md              # Implementation + review agent (universal)
│   │   ├── qa.md                    # Verification + review agent (universal)
│   │   └── memory/                  # Per-agent lesson logs
│   │       ├── architect-lessons.md
│   │       ├── engineer-lessons.md
│   │       └── qa-lessons.md
│   ├── skills/                      # On-demand skills (no base-context cost)
│   │   ├── pipeline/SKILL.md        # /pipeline — full Three Hats execution
│   │   ├── critique/SKILL.md        # /critique — design review only
│   │   └── scaffold/SKILL.md        # /scaffold — new project setup
│   └── rules/                       # Path-scoped rules (load only when relevant)
│       ├── mcp-server.md            # paths: mcp-server/**
│       ├── templates.md             # paths: templates/**
│       └── skills.md                # paths: .claude/skills/**, skills/**
├── templates/                       # Scaffolding templates
│   ├── CLAUDE.template.md           # Base CLAUDE.md with placeholders
│   └── agents/                      # Agent template variants
├── mcp-server/                      # Token-saving MCP tools
│   ├── pyproject.toml
│   └── src/
│       ├── server.py                # FastMCP entry point
│       └── tools/
│           ├── scaffold.py          # Generate project from template
│           ├── patterns.py          # Store/retrieve proven patterns
│           └── checklist.py         # Acceptance criteria runner
└── docs/
    ├── architecture.md
    └── token-optimization.md
```

## Milestones

- **M1:** Foundation — global CLAUDE.md, universal agents, per-agent memory, skills, hooks, rules **[DONE]**
- **M2:** MCP Server — FastMCP with scaffold + pattern + checklist tools **[DONE]**
- **M3:** Template System — parameterized project scaffolding from templates
- **M4:** Docs & validation — setup guide, token analysis, cross-project testing

## Domain Constraints

- Templates must work across project types (ML, web, CLI, data pipeline)
- Agent templates must be fully project-agnostic — project context comes from auto-loaded CLAUDE.md
- MCP tools must demonstrably reduce token usage
- All artifacts must be self-contained and composable
- Changes to universal templates must not break existing project setups
