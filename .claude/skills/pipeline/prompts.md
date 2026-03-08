# Agent Prompt Templates

Reference file for `/pipeline`. Read this file when constructing agent prompts.

## Architect

```
Read your instructions from: .claude/agents/architect.md
Read your lessons from: .claude/agents/memory/architect-lessons.md

TASK: [one paragraph describing what to design]

EXISTING FILES TO CONSIDER:
[list specific relevant file paths]
```

## Engineer (critique mode)

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

## QA (critique mode)

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

## Engineer (implementation mode)

```
Read your instructions from: .claude/agents/engineer.md
Read your lessons from: .claude/agents/memory/engineer-lessons.md

APPROVED PROPOSAL:
[paste the Final Proposal — all sections]

SOURCE FILES:
[list specific file paths to read or modify]
```

## QA (verification mode)

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
