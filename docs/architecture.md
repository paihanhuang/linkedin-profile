# System Architecture

## Overview

**claude-mcp** is infrastructure for optimizing Claude Code workflows across projects. It provides universal agent templates, a quality pipeline, MCP tools for token efficiency, and project scaffolding — all designed to be reusable across any project type.

```
┌─────────────────────────────────────────────────────────┐
│  Claude Code Session                                     │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Layer 1:     │  │ Layer 2:      │  │ Layer 3:       │  │
│  │ Global       │  │ Project       │  │ On-Demand      │  │
│  │ CLAUDE.md    │  │ CLAUDE.md     │  │ (agents,       │  │
│  │ (~4K chars)  │  │ (~3.9K chars) │  │  skills, rules,│  │
│  │ ALWAYS       │  │ AUTO per      │  │  MCP tools)    │  │
│  │ loaded       │  │ project       │  │ ONLY when      │  │
│  │              │  │               │  │ invoked        │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## The 3-Layer Context System

### Layer 1: Global Contract (`~/.claude/CLAUDE.md`)

Always loaded in every session, every project. Contains:
- Identity and communication style
- Core values and V-Model workflow
- Quality Pipeline pointer (agent table with templates and subagent types)
- Safety policy and memory discipline

**Cost:** ~4,006 chars (~1,000 tokens) per session.

### Layer 2: Project Contract (`./CLAUDE.md`)

Auto-loaded per project. Contains only project-specific context:
- Project name, description, goals
- Tech stack
- Project structure tree
- Milestones with completion status
- Domain constraints

**Cost:** ~3,891 chars (~970 tokens) per project session.

### Layer 3: On-Demand Components

Loaded only when needed — zero cost when not invoked:

| Component | Location | Trigger |
|-----------|----------|---------|
| Agents | `.claude/agents/*.md` | Spawned by pipeline |
| Skills | `.claude/skills/*/SKILL.md` | User invokes `/skill` |
| Rules | `.claude/rules/*.md` | Editing files matching path glob |
| MCP Tools | `mcp-server/src/tools/` | Tool call via MCP protocol |

## Quality Pipeline (Three Hats)

The pipeline runs non-trivial tasks through three specialized agents:

```
User Task
    │
    ▼
┌──────────┐     ┌──────────────────────────────┐
│ Architect │────▶│ Cross-Critique (parallel)     │
│ (Plan)    │     │  ┌───────────┐ ┌───────────┐ │
│           │     │  │ Engineer  │ │ QA        │ │
│ Design    │     │  │ (critique)│ │ (critique)│ │
│ draft     │     │  └───────────┘ └───────────┘ │
└──────────┘     └──────────┬───────────────────┘
                            │
                            ▼
                 ┌──────────────────┐
                 │ Claude Code      │
                 │ synthesizes      │
                 │ Final Proposal   │
                 └────────┬─────────┘
                          │
                     User Approves
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
    ┌──────────────┐       ┌──────────────┐
    │ Engineer     │──────▶│ QA           │
    │ (implement)  │       │ (verify)     │
    │              │       │              │
    │ Writes code  │       │ Runs checks  │
    └──────────────┘       └──────┬───────┘
                                  │
                           Update Memory
```

**Invocation:** `/pipeline <task>` (full pipeline) or `/critique <task>` (design review only)

**Autonomous mode:** `/autopilot` runs through milestones without user approval gates, with file-based stop signal (`touch .claude/STOP`).

**Key rules:**
- Artifacts passed verbatim between agents — never summarized
- Each agent runs in its own subagent context (isolated)
- Cross-critique is parallel (Engineer + QA evaluate simultaneously)

## Agent System

All agents are project-agnostic — they get project context from the auto-loaded CLAUDE.md.

| Agent | File | subagent_type | Modes |
|-------|------|---------------|-------|
| Architect | `.claude/agents/architect.md` | `Plan` | Design only |
| Engineer | `.claude/agents/engineer.md` | `general-purpose` | Critique, Implementation |
| QA | `.claude/agents/qa.md` | `general-purpose` | Critique, Verification |

**Required output sections:**
- Architect: ASSUMPTIONS, IN_SCOPE, OUT_OF_SCOPE, DESIGN, RISKS, ACCEPTANCE_CRITERIA
- Engineer: PATCH_PLAN, IMPLEMENTATION, CHANGED_FILES, VERIFY_STEPS, ROLLBACK_PLAN
- QA: PASS_CRITERIA, FAILURE_MODES, REMAINING_RISK, ACTION_ITEMS, REPRO_STEPS

### Agent Memory

Per-agent lesson logs in `.claude/agents/memory/`:
- `architect-lessons.md`, `engineer-lessons.md`, `qa-lessons.md`
- Append-only — entries added after each pipeline run
- Agents read their lessons before acting (injected via skill template)
- Prevents repeating mistakes across runs

## MCP Server

FastMCP server (`mcp-server/src/server.py`) with 6 registered tools:

### Pattern Tools (`src/tools/patterns.py`)
- `save_pattern(name, description, code, language, tags)` — upsert with validation
- `get_pattern(name)` — exact lookup
- `search_patterns(query?, language?, tag?)` — OR on name/description, AND across filter types
- `delete_pattern(name)` — remove by name

**Store:** Atomic JSON file (`~/.claude-mcp/patterns.json`) with `fcntl.flock` + `tempfile.mkstemp` + `os.rename`.

### Scaffold Tool (`src/tools/scaffold.py`)
- `scaffold_project(project_name, description, tech_stack, milestones, ...)` — generates complete project setup

**Process:** Load manifest → build placeholder map → for each entry: copy or render template → validate output.

### Checklist Tool (`src/tools/checklist.py`)
- `check_criteria(criteria, working_dir?)` — runs shell-based acceptance criteria checks

**Process:** `asyncio.create_subprocess_shell` with `start_new_session=True`, timeout via `asyncio.wait_for`, kills process group on timeout via `os.killpg`.

Exit code mapping: 0 = pass, 126/127 = error, other non-zero = fail.

## Template System

### Manifest (`templates/manifest.json`)

Declarative registry of all scaffold outputs. Each entry specifies:
- `id`: unique identifier
- `source`: template file path (relative to `templates/`)
- `output`: target file path (relative to project root)
- `mode`: `copy` (verbatim) or `render` (placeholder substitution)
- `render_vars`: optional per-entry placeholder overrides

### Template Engine (`src/template_engine.py`)

1. **Conditional blocks:** `{{#IF KEY}}...{{/IF KEY}}` — removed when value is empty/None
2. **Placeholder substitution:** `{{PLACEHOLDER}}` → value (single-pass via `re.sub`)
3. **Validation:** No `{{...}}` tokens remaining after rendering

Processing order: conditionals → substitution → blank line collapse → validation.

### Template Files

```
templates/
├── manifest.json              # Artifact registry
├── CLAUDE.template.md         # Main project CLAUDE.md (rendered)
├── agents/                    # Copied verbatim
│   ├── architect.md
│   ├── engineer.md
│   └── qa.md
├── hooks/                     # Copied verbatim
│   ├── guard-protected-files.sh
│   └── memory-reminder.sh
├── skills/                    # Copied verbatim
│   ├── pipeline-SKILL.md
│   └── critique-SKILL.md
├── settings.json              # Copied verbatim
└── memory-header.template.md  # Rendered per agent (AGENT_NAME)
```

## Hooks

Seven hooks registered in `.claude/settings.json`:

| Event | Script | Purpose |
|-------|--------|---------|
| `SessionStart` | `session-standup.sh` | Inject milestones, recent commits, agent lessons |
| `UserPromptSubmit` | `clarity-gate-check.sh` | Flag non-trivial requests for Clarity Gate |
| `PreToolUse[Edit\|Write]` | `guard-protected-files.sh` | Block edits to universal templates |
| `PreToolUse[Bash]` | `guard-dangerous-commands.sh` | Block destructive commands |
| `Stop` | `memory-reminder.sh` | Remind to update agent memory |
| `PreCompact` | `preserve-pipeline-state.sh` | Inject pipeline/autopilot state |
| `Notification` | `notify-send` | Desktop notification on prompts |

Hooks are deterministic (guaranteed execution) vs CLAUDE.md rules (advisory).

## Path-Scoped Rules

Rules in `.claude/rules/` load only when editing files matching their path globs:

| Rule | Scope | Content |
|------|-------|---------|
| `mcp-server.md` | `mcp-server/**` | FastMCP conventions, tool design patterns |
| `templates.md` | `templates/**` | Placeholder syntax, testing requirements |
| `skills.md` | `.claude/skills/**` | Skill format conventions |

## Data Flow

```
User Prompt
    │
    ├─[Hook: clarity-gate-check]─── Inject reminder if non-trivial
    │
    ▼
Claude Code (orchestrator)
    │
    ├─[/pipeline]──── Architect → Critique → Synthesize → Implement → Verify
    ├─[/critique]──── Architect → Critique → Synthesize (design review only)
    ├─[/autopilot]─── Loop: milestones × pipeline (autonomous)
    ├─[/scaffold]──── MCP tool call → scaffold_project() → template engine
    │
    ├─[MCP tools]──── save/get/search/delete patterns, check criteria
    │
    └─[Hook: memory-reminder]─── Remind to update lessons on Stop
```
