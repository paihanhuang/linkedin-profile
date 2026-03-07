---
name: pipeline
description: Run the Three Hats quality pipeline (Architect → cross-critique → Engineer → QA). Use for any non-trivial implementation task requiring design review.
user-invocable: true
---

# Pipeline Execution Protocol

Run the Three Hats pipeline for the task described in $ARGUMENTS.

## Recent Agent Lessons (auto-injected)

**Architect:**
!`tail -10 .claude/agents/memory/architect-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**Engineer:**
!`tail -10 .claude/agents/memory/engineer-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**QA:**
!`tail -10 .claude/agents/memory/qa-lessons.md 2>/dev/null || echo "(no lessons yet)"`

---

## Agent Prompt Templates

**Architect:**
```
Read your instructions from: .claude/agents/architect.md
Read your lessons from: .claude/agents/memory/architect-lessons.md

TASK: [one paragraph describing what to design]

EXISTING FILES TO CONSIDER:
[list specific relevant file paths]
```

**Engineer (critique mode):**
```
Read your instructions from: .claude/agents/engineer.md
Read your lessons from: .claude/agents/memory/engineer-lessons.md

MODE: CRITIQUE — do not implement. Evaluate this design for:
- Implementability: can this be built as specified?
- Ambiguity: are interfaces, data flows, and boundaries clear enough to code from?
- Complexity: is there a simpler approach?
- Maintainability: will this be debuggable and extensible?

ARCHITECT DRAFT:
[paste full architect output]
```

**QA (critique mode):**
```
Read your instructions from: .claude/agents/qa.md
Read your lessons from: .claude/agents/memory/qa-lessons.md

MODE: CRITIQUE — do not verify code. Evaluate this design for:
- Testability: can the acceptance criteria actually be verified?
- Coverage gaps: what failure modes or edge cases are missing?
- Risk blind spots: what could go wrong that the design doesn't address?
- Ambiguity in acceptance criteria: are pass/fail conditions concrete?

ARCHITECT DRAFT:
[paste full architect output]
```

**Engineer (implementation mode):**
```
Read your instructions from: .claude/agents/engineer.md
Read your lessons from: .claude/agents/memory/engineer-lessons.md

APPROVED PROPOSAL:
[paste the Final Proposal — all sections]

SOURCE FILES:
[list specific file paths to read or modify]
```

**QA (verification mode):**
```
Read your instructions from: .claude/agents/qa.md
Read your lessons from: .claude/agents/memory/qa-lessons.md

APPROVED PROPOSAL:
[paste the Final Proposal]

ENGINEER ARTIFACT:
[paste full engineer output]

CHANGED FILES:
[list files created or modified]
```

## Execution Steps

### Step 1: Architect Draft
1. Spawn `Agent(subagent_type=Plan)` with architect prompt
2. Validate all sections present: `ASSUMPTIONS`, `IN_SCOPE`, `OUT_OF_SCOPE`, `DESIGN`, `RISKS`, `ACCEPTANCE_CRITERIA`
3. If incomplete: re-spawn noting missing sections

### Step 2: Cross-Critique (parallel)
1. Spawn Engineer (critique) + QA (critique) **in parallel**
2. Collect both critiques

### Step 3: Synthesize & Propose
1. Review both critiques — identify valid concerns vs noise
2. Categorize each concern: **addressed** (revise design) or **dismissed** (with reasoning)
3. Produce **Final Proposal** containing:
   - Original design sections (revised where needed)
   - `ADDRESSED_CRITIQUES` section listing each concern and resolution
4. Present Final Proposal to Traso — **wait for approval**

### Step 4: Engineer Implements
1. Only after Traso approves
2. Spawn `Agent(subagent_type=general-purpose)` with engineer implementation prompt
3. Validate: `PATCH_PLAN`, `IMPLEMENTATION`, `CHANGED_FILES`, `VERIFY_STEPS`, `ROLLBACK_PLAN`
4. Check implementation matches approved DESIGN

### Step 5: QA Verifies
1. Spawn `Agent(subagent_type=general-purpose)` with QA verification prompt
2. Validate: `PASS_CRITERIA`, `FAILURE_MODES`, `REMAINING_RISK`, `ACTION_ITEMS`, `REPRO_STEPS`
3. **No blockers** → report success to Traso
4. **Blockers** → re-spawn Engineer with blocker details, then re-run QA
5. **Design flaw** → go back to Step 1 with QA's finding

### Step 6: Update Agent Memory
After pipeline completes (success or failure):
- Append lessons to the relevant agent memory files
- If QA found issues: update Engineer's memory with the finding
- If critique caught a real problem: update Architect's memory

## Rules

- Pass artifacts verbatim — never summarize or paraphrase
- Don't add commentary to agent prompts
- Don't pass file contents inline if the agent can read the file — pass paths
- Don't combine pipeline stages into one agent
- Don't skip the critique phase — it's how quality improves over time

## Skip Pipeline For

- Single-line fixes, typos, config changes
- Changes touching 1 file with < 20 lines
- If in doubt, ask Traso
