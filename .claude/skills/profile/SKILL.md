---
name: profile
description: Runs the LinkedIn Profile Builder pipeline (Strategist → cross-critique → Writer → Validator). Generates a high-impact LinkedIn profile from a resume and job targets.
user-invocable: true
---

# Profile Generation Pipeline

Generate a tailored LinkedIn profile for the task described in $ARGUMENTS.

## Inputs Required

1. **Resume:** `resume/resume.txt` (pre-parsed from PDF)
2. **Job Targets:** `config/job_targets.yaml`

If either file is missing, notify the user and STOP.

## Recent Agent Lessons (auto-injected)

**Strategist (Architect):**
!`tail -10 .claude/agents/memory/architect-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**Writer (Engineer):**
!`tail -10 .claude/agents/memory/engineer-lessons.md 2>/dev/null || echo "(no lessons yet)"`

**Validator (QA):**
!`tail -10 .claude/agents/memory/qa-lessons.md 2>/dev/null || echo "(no lessons yet)"`

---

## Progress Checklist

Copy into working notes and check off:

```
- [ ] Step 0: Load resume + job targets
- [ ] Step 1: Strategist research + blueprint
- [ ] Step 2: Cross-critique — Writer + Validator review blueprint
- [ ] Step 3: Synthesize → Final Blueprint
- [ ] Step 3b: User approved Final Blueprint
- [ ] Step 4: Writer generates profile
- [ ] Step 5: Validator verifies (web search, job matching, fact-check)
- [ ] Step 6: Final profile saved to output/
- [ ] Step 7: Agent memory updated
```

## Execution Steps

### Step 0: Load Inputs
1. Read `resume/resume.txt` — the parsed resume
2. Read `config/job_targets.yaml` — target roles and preferences
3. Validate both are non-empty and well-formed

### Step 1: Profile Strategist (Architect)
1. Use web search tools to research:
   - Recruiter search patterns for the target roles
   - Top LinkedIn profiles in similar positions
   - Current industry trends and in-demand skills
   - Compensation benchmarks for target roles
2. Produce the **Profile Blueprint** per `.claude/agents/architect.md`
3. Validate sections: `RECRUITER_SIGNALS`, `BENCHMARK_INSIGHTS`, `INDUSTRY_TRENDS`, `COMPENSATION_MAP`, `PROFILE_BLUEPRINT`, `TONE_AND_STYLE`, `KEYWORD_MAP`

### Step 2: Cross-Critique (parallel concepts, sequential execution)
1. **Writer critique:** Review the blueprint for writability, resume fit, keyword feasibility, character budget
2. **Validator critique:** Review the blueprint for verifiability, coverage gaps, risk blind spots
3. Collect both critiques

### Step 3: Synthesize & Propose
1. Categorize each concern: **addressed** (revise blueprint) or **dismissed** (with reasoning)
2. Produce **Final Blueprint** with `ADDRESSED_CRITIQUES` section
3. Present to user — **wait for approval**

### Step 4: Profile Writer (Engineer)
1. Only after user approves
2. Follow the approved blueprint exactly
3. Write all LinkedIn profile sections per `.claude/agents/engineer.md`
4. Self-verify: fact-check, character limits, keyword coverage, tone
5. Save generated profile to `output/profile_YYYYMMDD_HHMMSS.md`

### Step 5: Profile Validator (QA)
1. Fact-check every claim against the resume
2. Use web search to find 5-10 real job postings matching target roles
3. Score keyword overlap between profile and postings
4. Check ATS compatibility
5. Produce scorecard per `.claude/agents/qa.md`
6. **No blockers** → report success, save scorecard to `output/`
7. **Blockers** → return to Step 4 with specific fixes, then re-validate

### Step 6: Save Outputs
- Final profile: `output/profile_YYYYMMDD_HHMMSS.md`
- QA scorecard: `output/scorecard_YYYYMMDD_HHMMSS.md`

### Step 7: Update Agent Memory
- Append lessons to `.claude/agents/memory/architect-lessons.md`
- Append lessons to `.claude/agents/memory/engineer-lessons.md`
- Append lessons to `.claude/agents/memory/qa-lessons.md`

## Rules

- Pass artifacts verbatim — never summarize or paraphrase
- Don't combine pipeline stages
- Never skip the critique phase
- Every profile claim must trace to the resume
- Use web search for real-time data in Steps 1 and 5
