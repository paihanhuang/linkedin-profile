---
name: autopilot
description: Continuous autonomous execution — works through milestones unattended using the full pipeline (design, critique, implement, verify) with git checkpoints. Invoked before stepping away or for overnight runs. Stop remotely with `touch .claude/STOP`.
user-invocable: true
---

# Autopilot Mode

Autonomous execution with full permission to proceed without approval gates. Work continuously until all specified work is complete or a stop signal is detected.

Agent prompt templates: read `.claude/skills/pipeline/prompts.md`

## Inputs

- `$ARGUMENTS`: Scope of work — empty (all remaining milestones), a milestone ("M3"), or a task description.

## Current State (auto-injected)

**Progress:**
!`cat .claude/autopilot-progress.md 2>/dev/null || echo "(no prior autopilot run)"`

**Recent Lessons:**
!`tail -5 .claude/agents/memory/architect-lessons.md 2>/dev/null || echo "(none)"`
!`tail -5 .claude/agents/memory/engineer-lessons.md 2>/dev/null || echo "(none)"`
!`tail -5 .claude/agents/memory/qa-lessons.md 2>/dev/null || echo "(none)"`

---

## Before Starting

1. Read project `CLAUDE.md` for milestones and state
2. Read `.claude/autopilot-progress.md` if exists — **resume from where you left off**
3. Read agent memory files
4. Ensure git is initialized

## Per-Milestone Checklist

Copy and track for each milestone:

```
Milestone: [name]
- [ ] STOP check
- [ ] Phase 1: Design — Architect draft complete
- [ ] Phase 2: Critique — Engineer + QA parallel
- [ ] Phase 3: Synthesize — Final Proposal auto-approved
- [ ] STOP check
- [ ] Phase 4: Implement — code + tests passing
- [ ] Phase 5: Verify — QA pass (max 3 fix cycles)
- [ ] Phase 6: Checkpoint — git commit + memory update
```

## Progress File

Maintain `.claude/autopilot-progress.md` as durable state (survives compaction). **Update after every phase.**

Format:
```markdown
# Autopilot Progress

Started: YYYY-MM-DD HH:MM
Last updated: YYYY-MM-DD HH:MM

## Completed
- [x] M1: Description — completed YYYY-MM-DD
- [x] M2: Description — completed YYYY-MM-DD

## In Progress
- [ ] M3: Description — started YYYY-MM-DD
  - [x] Design complete
  - [x] Critique complete
  - [ ] Implementation in progress

## Remaining
- [ ] M4: Description

## Issues Encountered
- [description and resolution, or "needs user attention"]
```

## Stop Mechanism

Before each major phase: `test -f .claude/STOP && echo STOP`
- If STOP exists: commit work, update progress, report status, then `rm .claude/STOP`
- Create remotely: `touch .claude/STOP`

## Execution Loop

For each milestone:

### Phase 1: Design
Spawn Architect (`subagent_type: Plan`). Validate: ASSUMPTIONS, IN_SCOPE, OUT_OF_SCOPE, DESIGN, RISKS, ACCEPTANCE_CRITERIA.

### Phase 2: Cross-Critique
Spawn Engineer + QA critique **in parallel**.

### Phase 3: Synthesize & Auto-Approve
Categorize concerns (addressed/dismissed). Produce Final Proposal. **Auto-approve** — log decision in progress file.

### Phase 4: Implement
Implement directly. Run tests as you go. Update progress file.

### Phase 5: Verify
Spawn QA verification. Fix issues and re-verify (max 3 cycles). If still failing: log as unresolved, continue to next independent milestone.

### Phase 6: Checkpoint
`git add` + `git commit -m "autopilot: [milestone] — [summary]"`. Update agent memory and progress file.

## Error Handling

- **Test failures**: Fix and retry (max 3 attempts)
- **Unresolvable blockers**: Log in progress file, commit state, continue if possible
- **Context compaction**: Re-read progress file, CLAUDE.md, and agent memory

## Completion

1. Final commit if uncommitted changes
2. Update progress file with completion timestamp and summary:
   - What was completed
   - Issues encountered and resolutions
   - Items needing user attention (if any)
3. Output final status report

## Rules

- Never skip QA verification or critique phase
- Commit after each milestone (rollback points)
- Update progress file after every phase
- Check STOP file before each phase
- Do not push to remote — user reviews and pushes
- Do not delete or overwrite user work — if unexpected state, log it and skip
- Pass artifacts verbatim between agents
