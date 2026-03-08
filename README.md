# Claude Code Optimization Toolkit

Infrastructure for optimizing Claude Code workflows across projects: universal agent templates, quality pipeline, MCP tools for token efficiency, and project scaffolding.

## Installation

### 1. Unpack

```bash
mkdir ~/claude-mcp && cd ~/claude-mcp
unzip claude-code-toolkit.zip
```

### 2. Install global CLAUDE.md

```bash
mkdir -p ~/.claude
cp global-CLAUDE.md ~/.claude/CLAUDE.md
# Edit ~/.claude/CLAUDE.md — change "Traso" to your name, adjust timezone
```

### 3. Set up the MCP server

```bash
cd mcp-server
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

### 4. Register the MCP server

Add to `~/.claude.json` (create if it doesn't exist):

```json
{
  "mcpServers": {
    "claude-mcp": {
      "command": "/absolute/path/to/claude-mcp/mcp-server/.venv/bin/claude-mcp-server",
      "env": {
        "CLAUDE_MCP_TEMPLATES_DIR": "/absolute/path/to/claude-mcp/templates",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

`ANTHROPIC_API_KEY` is only needed for batch tools (`submit_batch`, `check_batch`, `get_batch_results`). Omit if not using batching.

## Quick Start: New Project Setup

### Option 1: MCP Scaffold Tool (recommended)

```
cd ~/new-project
claude
> /scaffold
```

It will ask for project name, description, tech stack, milestones, and domain constraints — then generate the full setup.

### Option 2: Manual Copy

```bash
cp -r ~/claude-mcp/.claude ~/new-project/.claude
cp ~/claude-mcp/.claude/skills/pipeline/prompts.md ~/new-project/.claude/skills/pipeline/
# Then create a project CLAUDE.md tailored to your project
```

### What You Get

```
new-project/
├── CLAUDE.md                        # Tailored to your project
├── .claude/
│   ├── agents/                      # Universal (no changes needed)
│   │   ├── architect.md             # Design agent
│   │   ├── engineer.md              # Implementation + review agent
│   │   ├── qa.md                    # Verification + review agent
│   │   └── memory/                  # Empty, ready for lessons
│   │       ├── architect-lessons.md
│   │       ├── engineer-lessons.md
│   │       └── qa-lessons.md
│   ├── skills/
│   │   ├── pipeline/SKILL.md        # /pipeline — full quality pipeline
│   │   └── critique/SKILL.md        # /critique — design review only
│   ├── hooks/                       # Guard + reminder hooks
│   │   ├── guard-protected-files.sh
│   │   └── memory-reminder.sh
│   └── settings.json                # Hooks wired up
```

The agents, skills, and hooks are **project-agnostic** — they work as-is. You only customize `CLAUDE.md` (project name, tech stack, milestones, constraints). Then `/pipeline` works immediately.

## Usage

### Quality Pipeline

For any non-trivial task:
```
/pipeline Build a REST API for user authentication
```

This runs the Three Hats pipeline:
1. **Architect** designs the solution (with acceptance criteria)
2. **Engineer + QA** critique the design in parallel
3. Claude Code synthesizes critiques into a Final Proposal
4. You approve → **Engineer** implements → **QA** verifies
5. Agent memory updated with lessons learned

### Design Review Only

```
/critique Evaluate adding WebSocket support to the dashboard
```

Runs Architect draft + cross-critique without implementation.

### Autonomous Mode

For unattended work (e.g., overnight):
```
/autopilot Complete remaining milestones M3 and M4
```

- Works through milestones without user approval gates
- Git commits after each milestone (rollback points)
- Progress tracked in `autopilot-progress.md`
- Stop gracefully: `touch .claude/STOP`
- Requires: `claude --dangerously-skip-permissions` or pre-allowed tools

### MCP Tools

When the MCP server is registered, Claude Code gains these tools:

| Tool | Purpose |
|------|---------|
| `save_pattern` | Store a reusable code pattern |
| `get_pattern` | Retrieve a pattern by name |
| `search_patterns` | Search patterns by query, language, or tag |
| `delete_pattern` | Remove a pattern |
| `scaffold_project` | Generate a new project setup from templates |
| `check_criteria` | Run shell-based acceptance criteria checks |
| `submit_batch` | Submit tasks to Message Batches API (50% cost) |
| `check_batch` | Check batch processing status |
| `get_batch_results` | Retrieve completed batch results |

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design.

**3-Layer Context System:**
- **Layer 1 — Global** (`~/.claude/CLAUDE.md`): Identity, workflow, pipeline pointer. Always loaded (~1,000 tokens).
- **Layer 2 — Project** (`./CLAUDE.md`): Project-specific context. Auto-loaded (~970 tokens).
- **Layer 3 — On-Demand**: Agents, skills, rules, MCP tools. Loaded only when invoked (zero base cost).

## Token Savings

See [docs/token-optimization.md](docs/token-optimization.md) for detailed analysis.

Estimated **~60,000-80,000 tokens saved per 20-turn session** compared to a monolithic approach, through context separation, on-demand skills, path-scoped rules, agent isolation, MCP tools, prompt caching (~90% on stable prefix), and Message Batches API (50% on non-urgent tasks).

## Development

```bash
cd mcp-server
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Run tests (PYTHONPATH="" needed if ROS packages are on system path)
PYTHONPATH="" .venv/bin/python -m pytest tests/ -v
```

104 tests across 2 test files:
- `test_scaffold.py` — template engine, manifest validation, scaffold edge cases
- `test_cross_project.py` — 4 project types (ML, web, CLI, data-pipeline), structural integrity

## Project Structure

```
claude-mcp/
├── CLAUDE.md                    # Project-specific context
├── .claude/                     # Claude Code configuration
│   ├── agents/                  # Universal agent templates + memory
│   ├── skills/                  # On-demand skills (pipeline, critique, scaffold, autopilot)
│   ├── hooks/                   # 7 deterministic hooks
│   ├── rules/                   # Path-scoped conventions
│   └── settings.json            # Hook registration
├── templates/                   # Scaffolding templates
│   ├── manifest.json            # Declarative artifact registry
│   ├── CLAUDE.template.md       # Base project CLAUDE.md
│   ├── agents/                  # Agent template copies
│   ├── hooks/                   # Hook script templates
│   ├── skills/                  # Skill stub templates
│   └── settings.json            # Default settings
├── mcp-server/                  # FastMCP server
│   ├── src/
│   │   ├── server.py            # Entry point (9 tools)
│   │   ├── template_engine.py   # Render, validate, manifest
│   │   └── tools/               # Pattern, scaffold, checklist, batch
│   └── tests/                   # 104 tests
└── docs/
    ├── architecture.md          # System design
    └── token-optimization.md    # Token analysis
```
