---
name: critique
description: Run only the cross-critique phase on a design document. Spawns Engineer + QA in parallel to review a design for implementability, testability, and risk blind spots.
user-invocable: true
context: fork
---

# Cross-Critique Protocol

Run a design critique on the provided design document or $ARGUMENTS.

## Steps

1. **Identify the design artifact** — the user should provide or point to the design to critique.

2. **Spawn Engineer critique + QA critique in parallel:**

**Engineer (critique mode):**
```
Read your instructions from: .claude/agents/engineer.md
Read your lessons from: .claude/agents/memory/engineer-lessons.md

MODE: CRITIQUE — do not implement. Evaluate this design for:
- Implementability: can this be built as specified?
- Ambiguity: are interfaces, data flows, and boundaries clear enough to code from?
- Complexity: is there a simpler approach?
- Maintainability: will this be debuggable and extensible?

DESIGN TO CRITIQUE:
[paste the design artifact]
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

DESIGN TO CRITIQUE:
[paste the design artifact]
```

3. **Synthesize critiques** — Review both outputs. For each finding:
   - **Addressed**: Valid concern — propose revision
   - **Dismissed**: Not applicable — state reasoning

4. **Present summary** to Traso with all findings and proposed resolutions.
