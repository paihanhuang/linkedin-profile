# CLAUDE.md - Project Operating Contract

## Project

**LinkedIn Profile Builder Agent** — multi-agent pipeline that generates a high-impact LinkedIn profile optimized for executive recruiter discovery and job matching, given a resume and target role preferences.

Goals:
1. Generate LinkedIn profiles that maximize recruiter search visibility
2. Tailor content to specific VP/C-suite target roles
3. Validate discoverability against real job postings via web research
4. Produce actionable, copy-paste-ready profile content

## Tech Stack

- **Language:** Python 3.11+
- **PDF Parsing:** PyMuPDF (fitz)
- **LLM:** Agent-native (uses the orchestrating agent directly)
- **Web Research:** Agent-native (uses agent's search/browser tools)
- **Config:** YAML for job targets and settings
- **No heavy external deps** unless justified

## Project Structure

```
linkedin-profile/
├── CLAUDE.md                        # Project-specific context
├── resume/                          # User resume(s)
│   └── *.pdf                        # Source resume files
├── config/
│   └── job_targets.yaml             # Target roles and preferences
├── src/
│   ├── resume_parser.py             # PDF → structured resume data
│   ├── profile_formatter.py         # Profile output formatting
│   └── scoring.py                   # Keyword overlap scoring
├── output/                          # Generated profiles + scorecards
├── .claude/
│   ├── agents/
│   │   ├── architect.md             # Profile Strategist
│   │   ├── engineer.md              # Profile Writer
│   │   ├── qa.md                    # Profile Validator
│   │   └── memory/                  # Per-agent lesson logs
│   ├── skills/
│   │   └── profile/SKILL.md         # /profile pipeline orchestration
│   └── settings.json                # Hooks configuration
├── mcp-server/                      # MCP tools (inherited)
└── docs/
```

## Milestones

- **M1:** Foundation — agent templates, pipeline skill, resume parser, config schema **[IN PROGRESS]**
- **M2:** End-to-end run — generate first profile using pipeline **[PLANNED]**
- **M3:** QA validation — web search scoring against real postings **[PLANNED]**
- **M4:** Polish — iteration, multi-target support, output quality **[PLANNED]**

## Domain Constraints

- All profile claims must be traceable to the resume (no fabrication)
- LinkedIn character limits must be enforced (headline ≤220, summary ≤2600)
- Tone must match executive/VP-level positioning
- Keywords must be incorporated naturally, not stuffed
- Agent templates must follow the Three Hats pattern
