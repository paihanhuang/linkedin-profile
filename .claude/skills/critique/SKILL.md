---
name: critique
description: Runs only the cross-critique phase on a design or proposal. Spawns Engineer + QA in parallel for implementability, testability, and risk review. Use when reviewing a design without running the full pipeline.
user-invocable: true
context: fork
---

# Cross-Critique Protocol

Run a design critique on the provided design document or $ARGUMENTS.

Agent prompt templates: read `.claude/skills/pipeline/prompts.md` (critique mode sections)

## Steps

1. **Identify the design artifact** — the user provides or points to the design.

2. **Spawn Engineer critique + QA critique in parallel** using critique mode prompts from `prompts.md`.

3. **Synthesize critiques** — for each finding:
   - **Addressed**: Valid concern — propose revision
   - **Dismissed**: Not applicable — state reasoning

4. **Present summary** to Traso with all findings and proposed resolutions.
