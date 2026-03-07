"""Project scaffolding tool — generate a complete Claude Code project setup from templates."""

import json
import logging
import os
import re
import shutil
from pathlib import Path

from src.config import resolve_templates_dir

logger = logging.getLogger(__name__)

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def scaffold_project(
    project_name: str,
    description: str,
    tech_stack: str,
    milestones: list[str],
    domain_constraints: list[str] | None = None,
    output_dir: str | None = None,
    force: bool = False,
) -> dict:
    """Generate a complete Claude Code project setup from templates.

    Creates CLAUDE.md, agent templates, memory files, pipeline skill,
    and settings.json in the target directory.
    """
    logger.info("scaffold_project: project_name=%s, output_dir=%s", project_name, output_dir)

    # Validate project_name
    if not isinstance(project_name, str) or not project_name.strip():
        return {"error": "Missing or empty field: project_name",
                "details": {"field": "project_name"}}
    if not NAME_PATTERN.match(project_name):
        return {"error": "Invalid project_name: must match ^[a-z0-9][a-z0-9-]*$",
                "details": {"project_name": project_name}}

    # Validate other required fields
    for field_name, value in [("description", description), ("tech_stack", tech_stack)]:
        if not isinstance(value, str) or not value.strip():
            return {"error": f"Missing or empty field: {field_name}",
                    "details": {"field": field_name}}

    if not isinstance(milestones, list) or len(milestones) == 0:
        return {"error": "Missing or empty field: milestones",
                "details": {"field": "milestones"}}

    # Resolve templates directory
    templates_dir = resolve_templates_dir()
    if templates_dir is None:
        return {"error": "Templates directory not found",
                "details": {"hint": "Set CLAUDE_MCP_TEMPLATES_DIR environment variable"}}

    template_file = templates_dir / "CLAUDE.template.md"
    if not template_file.exists():
        return {"error": "Template file not found",
                "details": {"path": str(template_file)}}

    agents_dir = templates_dir / "agents"
    if not agents_dir.is_dir():
        return {"error": "Agent templates directory not found",
                "details": {"path": str(agents_dir)}}

    # Resolve output directory
    target = Path(output_dir) if output_dir else Path.cwd()
    target.mkdir(parents=True, exist_ok=True)

    files_created: list[str] = []
    warnings: list[str] = []

    def _write_file(rel_path: str, content: str) -> None:
        """Write a file, respecting force flag."""
        full_path = target / rel_path
        if full_path.exists() and not force:
            warnings.append(f"Skipped existing file: {rel_path}")
            return
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        files_created.append(rel_path)

    def _copy_file(src: Path, rel_path: str) -> None:
        """Copy a file verbatim, respecting force flag."""
        full_path = target / rel_path
        if full_path.exists() and not force:
            warnings.append(f"Skipped existing file: {rel_path}")
            return
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(full_path))
        files_created.append(rel_path)

    # Format milestones as markdown list
    milestones_md = "\n".join(f"- **M{i+1}:** {m}" for i, m in enumerate(milestones))

    # Format domain constraints
    if domain_constraints and len(domain_constraints) > 0:
        constraints_md = "\n".join(f"- {c}" for c in domain_constraints)
    else:
        constraints_md = "None specified"

    # Build project structure listing
    structure_lines = [
        f"{project_name}/",
        f"├── CLAUDE.md",
        f"├── .claude/",
        f"│   ├── settings.json",
        f"│   ├── hooks/",
        f"│   │   ├── guard-protected-files.sh",
        f"│   │   └── memory-reminder.sh",
        f"│   ├── agents/",
        f"│   │   ├── architect.md",
        f"│   │   ├── engineer.md",
        f"│   │   ├── qa.md",
        f"│   │   └── memory/",
        f"│   │       ├── architect-lessons.md",
        f"│   │       ├── engineer-lessons.md",
        f"│   │       └── qa-lessons.md",
        f"│   └── skills/",
        f"│       ├── pipeline/",
        f"│       │   └── SKILL.md",
        f"│       └── critique/",
        f"│           └── SKILL.md",
    ]
    structure_md = "\n".join(structure_lines)

    # Read and process template — single-pass replacement to prevent injection
    template_content = template_file.read_text(encoding="utf-8")

    placeholder_map = {
        "PROJECT_NAME": project_name,
        "PROJECT_DESCRIPTION": description,
        "TECH_STACK": tech_stack,
        "MILESTONES": milestones_md,
        "DOMAIN_CONSTRAINTS": constraints_md,
        "PROJECT_STRUCTURE": structure_md,
    }

    def _replace_placeholder(match: re.Match) -> str:
        key = match.group(1)
        return placeholder_map.get(key, match.group(0))

    claude_md = re.sub(r"\{\{(\w+)\}\}", _replace_placeholder, template_content)

    # Write CLAUDE.md
    _write_file("CLAUDE.md", claude_md)

    # Copy agent templates verbatim
    for agent_file in ["architect.md", "engineer.md", "qa.md"]:
        src = agents_dir / agent_file
        if src.exists():
            _copy_file(src, f".claude/agents/{agent_file}")
        else:
            warnings.append(f"Agent template not found: {agent_file}")

    # Create empty memory files with header comments
    memory_header = (
        "# {agent} Lessons\n\n"
        "<!-- Append entries after each pipeline run. Format:\n"
        "## [Date] — [Task Summary]\n"
        "- **Action:** What was implemented\n"
        "- **Outcome:** What happened\n"
        "- **Lesson:** What to remember next time\n"
        "-->\n"
    )
    for agent in ["Architect", "Engineer", "QA"]:
        filename = f"{agent.lower()}-lessons.md"
        _write_file(f".claude/agents/memory/{filename}", memory_header.format(agent=agent))

    # Copy or generate pipeline skill
    pipeline_src = templates_dir.parent / ".claude" / "skills" / "pipeline" / "SKILL.md"
    if pipeline_src.exists():
        _copy_file(pipeline_src, ".claude/skills/pipeline/SKILL.md")
    else:
        # Generate minimal pipeline skill
        minimal_pipeline = (
            "---\n"
            "name: pipeline\n"
            "description: Run the Three Hats quality pipeline "
            "(Architect -> Engineer -> QA).\n"
            "user-invocable: true\n"
            "---\n\n"
            "# Pipeline Execution Protocol\n\n"
            "Run the Three Hats pipeline for the task described in $ARGUMENTS.\n"
        )
        _write_file(".claude/skills/pipeline/SKILL.md", minimal_pipeline)

    # Create hook script stubs referenced by settings.json
    guard_hook = (
        "#!/usr/bin/env bash\n"
        "# Guard protected files from accidental edits.\n"
        "# Customize the PROTECTED_PATTERNS array for your project.\n"
        "PROTECTED_PATTERNS=(\n"
        '  ".claude/agents/*.md"\n'
        '  ".claude/skills/*/SKILL.md"\n'
        ")\n"
        "exit 0\n"
    )
    _write_file(".claude/hooks/guard-protected-files.sh", guard_hook)

    memory_hook = (
        "#!/usr/bin/env bash\n"
        "# Reminder to update agent memory after pipeline runs.\n"
        'echo "Reminder: Update agent memory files if lessons were learned."\n'
        "exit 0\n"
    )
    _write_file(".claude/hooks/memory-reminder.sh", memory_hook)

    # Copy or generate critique skill
    critique_src = templates_dir.parent / ".claude" / "skills" / "critique" / "SKILL.md"
    if critique_src.exists():
        _copy_file(critique_src, ".claude/skills/critique/SKILL.md")
    else:
        minimal_critique = (
            "---\n"
            "name: critique\n"
            "description: Run design review only "
            "(Architect draft + cross-critique, no implementation).\n"
            "user-invocable: true\n"
            "---\n\n"
            "# Design Critique Protocol\n\n"
            "Run a design review for the task described in $ARGUMENTS.\n"
        )
        _write_file(".claude/skills/critique/SKILL.md", minimal_critique)

    # Generate default settings.json
    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "bash .claude/hooks/guard-protected-files.sh"
                        }
                    ]
                }
            ],
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "bash .claude/hooks/memory-reminder.sh"
                        }
                    ]
                }
            ]
        }
    }
    _write_file(".claude/settings.json", json.dumps(settings, indent=2) + "\n")

    return {
        "status": "created",
        "project_name": project_name,
        "output_dir": str(target),
        "files_created": files_created,
        "warnings": warnings,
    }
