# Token Optimization Analysis

All token estimates use the heuristic: **1 token ~ 4 characters** for English prose and code. Actual tokenization varies by content type. Numbers are approximate and derived from measured file sizes (`wc -c`).

## Baseline: Without This Toolkit

In a naive setup, all context lives in a single large CLAUDE.md:
- Agent instructions, pipeline protocol, project context, coding conventions — everything in one file
- Typical size for a well-documented project: 12,000-20,000 characters (~3,000-5,000 tokens)
- Loaded every turn, every session

## Optimization 1: 3-Layer Context Separation

Split context into always-loaded (small) and on-demand (large) components.

| Layer | File | Chars | ~Tokens | When Loaded |
|-------|------|------:|--------:|-------------|
| Global | `~/.claude/CLAUDE.md` | 4,006 | 1,000 | Every session |
| Project | `./CLAUDE.md` | 3,891 | 970 | Per project |
| **Base context total** | | **7,897** | **~1,970** | |

**Savings:** Agent templates, skills, rules, and MCP tool schemas are NOT in the base context. A naive approach would load ~15,000+ tokens. The 3-layer system loads ~2,000 tokens as base context — **~13,000 tokens saved per turn**.

## Optimization 2: Skills On-Demand

Skills load only when invoked via `/skill` — zero cost in most turns.

| Skill | Chars | ~Tokens |
|-------|------:|--------:|
| `/pipeline` | 4,768 | 1,190 |
| `/autopilot` | 5,571 | 1,390 |
| `/critique` | 1,803 | 450 |
| `/scaffold` | 1,809 | 450 |
| **Total if all loaded** | **13,951** | **~3,480** |

Most turns don't invoke any skill. **~3,480 tokens saved in non-pipeline turns.**

## Optimization 3: Path-Scoped Rules

Rules load only when editing files matching their path globs.

| Rule | Scope | Chars | ~Tokens |
|------|-------|------:|--------:|
| `mcp-server.md` | `mcp-server/**` | 638 | 160 |
| `templates.md` | `templates/**` | 598 | 150 |
| `skills.md` | `.claude/skills/**` | 589 | 147 |
| **Total** | | **1,825** | **~457** |

When editing a README or docs, none of these load. **~457 tokens saved in most turns.**

## Optimization 4: Agent Subagent Isolation

Each pipeline agent runs in its own subagent context — only its template is loaded, not all three.

| Agent | Chars | ~Tokens |
|-------|------:|--------:|
| Architect | 2,024 | 506 |
| Engineer | 2,558 | 640 |
| QA | 2,483 | 621 |
| **Total if all loaded simultaneously** | **7,065** | **~1,766** |

With isolation, each stage sees only its own ~500-640 tokens (plus CLAUDE.md). **~1,100 tokens saved per pipeline stage** compared to loading all agents at once.

## Optimization 5: MCP Tools vs Re-Scanning

MCP tool calls return structured results without Claude needing to scan files or run commands manually.

| Operation | Without MCP | With MCP | Savings |
|-----------|------------:|----------:|--------:|
| Find matching patterns | Read file + filter (~1,500) | `search_patterns()` (~200) | ~1,300 |
| Scaffold a project | 12 file writes + mkdir (~3,000) | `scaffold_project()` (~300) | ~2,700 |
| Run acceptance checks | Multiple bash calls (~2,000) | `check_criteria()` (~250) | ~1,750 |
| Save a code pattern | Read store + edit + write (~800) | `save_pattern()` (~150) | ~650 |

Token estimates include tool schema overhead (~100 tokens) and result envelope.

## Optimization 6: Agent Memory

Small persistent files prevent repeating discovered lessons.

| Memory File | Chars | ~Tokens |
|-------------|------:|--------:|
| `architect-lessons.md` | 1,624 | 406 |
| `engineer-lessons.md` | 1,503 | 376 |
| `qa-lessons.md` | 2,136 | 534 |

Without memory, agents re-discover lessons through trial and error — typically costing 1,000-5,000 tokens per pipeline run in wasted exploration. Memory files are loaded only by the specific agent that reads them (via subagent context).

**Savings:** ~1,000-5,000 tokens per pipeline run.

## Optimization 7: Hooks (Deterministic Behavior)

Hooks inject reminders and guards without spending tokens on Claude "remembering" to check.

| Hook | Trigger | Estimated Savings |
|------|---------|------------------:|
| Clarity Gate | Non-trivial prompts | 500-2,000 per ambiguous request |
| Guard files | Edit/Write protected files | Prevents recovery cost (1,000+) |
| Guard commands | Dangerous bash commands | Prevents recovery cost (1,000+) |
| Memory reminder | Pipeline completion | Prevents forgotten lessons |
| Pipeline state | Pre-compaction | 1,000-3,000 per compaction |
| Session standup | Session start | Prevents context re-discovery |

Hooks execute deterministically — CLAUDE.md rules are advisory and may be forgotten under context pressure.

## Optimization 8: Prompt Caching

Claude Code automatically caches the system prompt prefix across turns. Content that stays stable between turns is read from cache (at ~90% reduced cost) instead of being re-processed.

**How the 3-layer architecture maximizes cache hits:**

```
Cached (stable across turns)          Variable (changes each turn)
┌──────────────────────────┐          ┌────────────────────────┐
│ Layer 1: Global CLAUDE.md│          │ User messages          │
│ (~1,000 tokens)          │          │ Tool results           │
│                          │          │ Agent outputs          │
│ Layer 2: Project CLAUDE.md          │ File contents          │
│ (~970 tokens)            │          │                        │
│                          │          │                        │
│ Tool definitions (MCP)   │          │                        │
│ (~600 tokens)            │          │                        │
└──────────────────────────┘          └────────────────────────┘
        ~2,570 tokens                     Varies per turn
        cached automatically
```

**Cache hit requirements:**
- Content must be an exact prefix match — any edit to CLAUDE.md invalidates the cache for that session
- Minimum cacheable size: 1,024 tokens (Sonnet) or 2,048 tokens (Opus)
- Combined global + project CLAUDE.md (~1,970 tokens) meets the threshold for most models
- Tool definitions are appended to the system prompt and also cached

**Best practices for maximizing cache hits:**

1. **Keep CLAUDE.md stable** — avoid editing it mid-session. Make changes between sessions.
2. **Put stable content first** — identity, values, workflow rules before milestones or status.
3. **Move volatile content out of CLAUDE.md** — progress tracking, current task state, and TODO lists belong in separate files read on demand, not in the always-loaded CLAUDE.md.
4. **Use hooks for state injection** — the `SessionStart` hook injects current state (recent commits, milestones) without polluting the cached system prompt.
5. **Don't duplicate MCP tool descriptions in CLAUDE.md** — tool schemas are already in the system prompt via MCP registration.

**Estimated savings from caching:**

| Content | Tokens | Cache Savings (90%) |
|---------|-------:|--------------------:|
| Global CLAUDE.md | 1,000 | 900/turn |
| Project CLAUDE.md | 970 | 873/turn |
| Tool definitions | ~600 | 540/turn |
| **Total** | **~2,570** | **~2,313/turn** |

Over a 20-turn session: **~46,000 tokens saved** from caching alone.

## Optimization 9: Message Batches API (50% Cost Savings)

The Anthropic Message Batches API processes requests at **50% reduced cost** in exchange for asynchronous delivery (typically minutes, guaranteed within 24 hours).

**MCP tools:** `submit_batch`, `check_batch`, `get_batch_results`

**Pipeline tasks suitable for batching:**

| Task | Typical Tokens | Batch Savings (50%) |
|------|---------------:|--------------------:|
| Engineer critique | ~2,000 | ~1,000 |
| QA critique | ~2,000 | ~1,000 |
| QA verification | ~3,000 | ~1,500 |
| Documentation review | ~1,500 | ~750 |

**Example: Cross-critique phase**

Instead of spawning 2 subagents interactively (~4,000 tokens at full price), submit both critiques as a batch:
```
submit_batch([
  {"id": "eng-critique", "prompt": "...", "system": "..."},
  {"id": "qa-critique",  "prompt": "...", "system": "..."}
])
```
Cost: ~2,000 tokens (50% of 4,000). Results ready in minutes.

**When to batch:** Any parallel, independent subtask that doesn't block the current conversation and can wait up to 1 hour.

**When NOT to batch:** Interactive work, sequential dependencies, tasks needing immediate response.

## Summary

| Optimization | Tokens Saved | When |
|---|--:|---|
| Context separation | ~13,000 | Every turn |
| Skills on-demand | ~3,480 | Most turns (no skill invoked) |
| Path-scoped rules | ~457 | Most turns (no rule-matching edits) |
| Agent isolation | ~1,100 | Each pipeline stage |
| MCP tools | 650-2,700 | Each tool use |
| Agent memory | 1,000-5,000 | Each pipeline run |
| Hooks | 500-3,000 | Each trigger event |
| Prompt caching | ~2,313 | Every turn (after first) |
| Message batches | 50% of batch | Non-urgent parallel tasks |

**Estimated total savings per typical 20-turn session:** ~60,000-80,000 tokens compared to a monolithic, uncached approach.

The primary savings come from prompt caching (stable system prompt cached at 90% discount), context separation (agents, skills, and rules not in base context), and MCP tools (single tool calls replacing multi-step operations). These optimizations compound across turns.
