---
name: autopilot
description: Continuous autonomous execution — works through milestones without user intervention. Invoke before stepping away. Creates git checkpoints after each milestone.
user-invocable: true
---

# Autopilot Mode

You are entering autonomous execution mode. The user has granted full permission to proceed without approval gates. Work continuously through the project until all specified work is complete or a stop signal is detected.

## Inputs

- `$ARGUMENTS`: Scope of work. Can be:
  - Empty → all remaining milestones from project CLAUDE.md
  - A specific milestone (e.g., "M3")
  - A task description (e.g., "add pagination to search_patterns")

## Current State (auto-injected)

**Progress:**
!`cat .claude/autopilot-progress.md 2>/dev/null || echo "(no prior autopilot run)"`

**Recent Lessons:**
!`tail -5 .claude/agents/memory/architect-lessons.md 2>/dev/null || echo "(none)"`
!`tail -5 .claude/agents/memory/engineer-lessons.md 2>/dev/null || echo "(none)"`
!`tail -5 .claude/agents/memory/qa-lessons.md 2>/dev/null || echo "(none)"`

---

## Before Starting

1. Read project `CLAUDE.md` to understand milestones and current state
2. Read `.claude/autopilot-progress.md` if it exists — **resume from where you left off**
3. Read all agent memory files for accumulated lessons
4. Ensure git is initialized (`git init` if needed)
5. Determine the work scope from `$ARGUMENTS`

## Progress File

Maintain `autopilot-progress.md` in the project root as durable state. This file survives context compaction and enables resume. **Update it after every phase**, not just after milestones.

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

Before each major phase, run: `test -f .claude/STOP && echo STOP`

- If STOP file exists: **stop gracefully** — commit current work, update progress file, report what was completed and what remains.
- User can create this file remotely: `touch .claude/STOP`
- After stopping, remove the file: `rm .claude/STOP`

## Execution Loop

For each milestone (or scoped task):

### Phase 1: Design
1. Check for STOP file
2. Spawn Architect subagent (`subagent_type: Plan`) with milestone requirements
3. Validate output has all required sections (ASSUMPTIONS, IN_SCOPE, OUT_OF_SCOPE, DESIGN, RISKS, ACCEPTANCE_CRITERIA)
4. If incomplete, re-spawn noting missing sections

### Phase 2: Cross-Critique
1. Spawn Engineer (critique) + QA (critique) **in parallel**
2. Collect both critiques

### Phase 3: Synthesize & Auto-Approve
1. Review critiques — identify valid concerns vs noise
2. Categorize each: **addressed** (revise design) or **dismissed** (with reasoning)
3. Produce Final Proposal with ADDRESSED_CRITIQUES section
4. **Auto-approve** — do NOT wait for user. Log the decision in progress file.
5. Update progress file: design phase complete

### Phase 4: Implement
1. Check for STOP file
2. Implement the approved design directly (you have full file access)
3. Run tests and checks as you go
4. Update progress file: implementation complete

### Phase 5: Verify
1. Spawn QA subagent to verify against acceptance criteria
2. If QA finds issues:
   - Fix them directly
   - Re-run verification
   - **Max 3 fix-verify cycles** per milestone
   - If still failing after 3 cycles: log as unresolved, commit current state, continue to next milestone if independent
3. Update progress file: verification complete

### Phase 6: Checkpoint
1. `git add` relevant files (not .env, credentials, or large binaries)
2. `git commit -m "autopilot: [milestone] — [summary]"`
3. Update agent memory files with lessons learned
4. Update progress file: milestone complete
5. Check for STOP file before continuing to next milestone

## Error Handling

- **Test failures**: Fix and retry (max 3 attempts per issue)
- **Critique concerns**: Incorporate and proceed (no user gate needed)
- **Unresolvable blockers**: Log in progress file under "Issues Encountered", commit current state, continue to next independent milestone or stop if blocked
- **Context compaction**: Progress file is your durable state — re-read it after compaction to know exactly where you left off. Re-read CLAUDE.md and agent memory too.

## Completion

When all work is complete:
1. Final git commit if any uncommitted changes
2. Update progress file with completion timestamp
3. Append a summary section to progress file:
   - What was completed
   - Issues encountered and resolutions
   - Items needing user attention (if any)
4. Output a final status report

## Rules

- **Never skip QA verification** — quality is non-negotiable even in autonomous mode
- **Never skip the critique phase** — it catches real issues
- **Commit after each milestone** — these are rollback points
- **Update progress file after every phase** — it's your lifeline after compaction
- **Check STOP file before each phase** — respect the shutdown signal
- **Do not push to remote** — only local commits; the user reviews and pushes
- **Do not delete or overwrite user work** — if you encounter unexpected state, log it and skip
- **Pass artifacts verbatim between agents** — never summarize
