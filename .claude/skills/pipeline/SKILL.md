---
name: pipeline
description: Runs the Three Hats quality pipeline (Architect → cross-critique → Engineer → QA). Invoked for non-trivial implementation tasks, new features, refactors, or multi-file changes that benefit from design review.
user-invocable: true
---

# Pipeline Execution Protocol

Run the Three Hats pipeline for the task described in $ARGUMENTS.

Agent prompt templates: read `.claude/skills/pipeline/prompts.md`

## Recent Agent Lessons (auto-injected)

**Architect:**
!`tail -10 .claude/agents/memory/architect-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**Engineer:**
!`tail -10 .claude/agents/memory/engineer-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**QA:**
!`tail -10 .claude/agents/memory/qa-lessons.md 2>/dev/null || echo "(no lessons yet)"`

---

## Progress Checklist

Copy this into your working notes and check off each step:

```
- [ ] Step 1: Architect draft — all sections present
- [ ] Step 2: Cross-critique — Engineer + QA in parallel
- [ ] Step 3: Synthesize — Final Proposal produced
- [ ] Step 3b: User approved Final Proposal
- [ ] Step 4: Engineer implements
- [ ] Step 5: QA verifies — no blockers
- [ ] Step 6: Agent memory updated
```

## Execution Steps

### Step 1: Architect Draft
1. Spawn `Agent(subagent_type=Plan)` with architect prompt
2. Validate sections: `ASSUMPTIONS`, `IN_SCOPE`, `OUT_OF_SCOPE`, `DESIGN`, `RISKS`, `ACCEPTANCE_CRITERIA`
3. If incomplete: re-spawn noting missing sections

### Step 2: Cross-Critique (parallel)
1. Spawn Engineer (critique) + QA (critique) **in parallel**
2. Collect both critiques

### Step 3: Synthesize & Propose
1. Categorize each concern: **addressed** (revise design) or **dismissed** (with reasoning)
2. Produce **Final Proposal** with `ADDRESSED_CRITIQUES` section
3. Present to Traso — **wait for approval**

### Step 4: Engineer Implements
1. Only after Traso approves
2. Spawn `Agent(subagent_type=general-purpose)` with engineer implementation prompt
3. Validate: `PATCH_PLAN`, `IMPLEMENTATION`, `CHANGED_FILES`, `VERIFY_STEPS`, `ROLLBACK_PLAN`
4. Check implementation matches approved DESIGN — flag deviations

### Step 5: QA Verifies
1. Spawn `Agent(subagent_type=general-purpose)` with QA verification prompt
2. Validate: `PASS_CRITERIA`, `FAILURE_MODES`, `REMAINING_RISK`, `ACTION_ITEMS`, `REPRO_STEPS`
3. **No blockers** → report success
4. **Blockers** → re-spawn Engineer with details, then re-run QA
5. **Design flaw** → go back to Step 1

### Step 6: Update Agent Memory
- If QA found issues: update Engineer's memory with the finding
- If critique caught a real problem: update Architect's memory
- Append general lessons to relevant agent memory files

## Rules

- Pass artifacts verbatim — never summarize or paraphrase
- Don't pass file contents inline if the agent can read the file — pass paths
- Don't add commentary to agent prompts
- Don't combine pipeline stages into one agent
- Never skip the critique phase

## Skip Pipeline For

- Single-line fixes, typos, config changes
- Changes touching 1 file with < 20 lines
- If in doubt, ask Traso
