"""Project scaffolding tool — generate a complete Claude Code project setup from templates."""

import logging
import re
import shutil
from pathlib import Path

from src.config import resolve_templates_dir
from src.template_engine import TemplateError, load_manifest, render_template

logger = logging.getLogger(__name__)

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _build_structure_tree(project_name: str) -> str:
    """Build the project directory tree string."""
    lines = [
        f"{project_name}/",
        "├── CLAUDE.md",
        "├── .claude/",
        "│   ├── settings.json",
        "│   ├── hooks/",
        "│   │   ├── guard-protected-files.sh",
        "│   │   └── memory-reminder.sh",
        "│   ├── agents/",
        "│   │   ├── architect.md",
        "│   │   ├── engineer.md",
        "│   │   ├── qa.md",
        "│   │   └── memory/",
        "│   │       ├── architect-lessons.md",
        "│   │       ├── engineer-lessons.md",
        "│   │       └── qa-lessons.md",
        "│   └── skills/",
        "│       ├── pipeline/",
        "│       │   └── SKILL.md",
        "│       └── critique/",
        "│           └── SKILL.md",
    ]
    return "\n".join(lines)


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

    # Load and validate manifest
    try:
        manifest = load_manifest(templates_dir)
    except TemplateError as e:
        return {"error": str(e), "details": {"type": "manifest_error"}}

    # Resolve output directory
    target = Path(output_dir) if output_dir else Path.cwd()
    target.mkdir(parents=True, exist_ok=True)

    files_created: list[str] = []
    warnings: list[str] = []

    def _write_file(rel_path: str, content: str) -> None:
        full_path = target / rel_path
        if full_path.exists() and not force:
            warnings.append(f"Skipped existing file: {rel_path}")
            return
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        files_created.append(rel_path)

    def _copy_file(src: Path, rel_path: str) -> None:
        full_path = target / rel_path
        if full_path.exists() and not force:
            warnings.append(f"Skipped existing file: {rel_path}")
            return
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(full_path))
        files_created.append(rel_path)

    # Build global placeholder map
    milestones_md = "\n".join(f"- **M{i+1}:** {m}" for i, m in enumerate(milestones))
    constraints_md = "\n".join(f"- {c}" for c in domain_constraints) if domain_constraints else ""
    structure_md = _build_structure_tree(project_name)

    global_placeholders = {
        "PROJECT_NAME": project_name,
        "PROJECT_DESCRIPTION": description,
        "TECH_STACK": tech_stack,
        "MILESTONES": milestones_md,
        "DOMAIN_CONSTRAINTS": constraints_md,
        "PROJECT_STRUCTURE": structure_md,
    }

    # Process each manifest entry
    for entry in manifest["templates"]:
        mode = entry["mode"]
        source = templates_dir / entry["source"]
        output_path = entry["output"]

        if mode == "copy":
            _copy_file(source, output_path)
        elif mode == "render":
            # Merge global placeholders with entry-specific render_vars
            placeholders = {**global_placeholders, **entry.get("render_vars", {})}
            content = source.read_text(encoding="utf-8")
            try:
                rendered = render_template(content, placeholders, source_name=entry["source"])
            except TemplateError as e:
                return {"error": str(e), "details": {"entry": entry["id"]}}
            _write_file(output_path, rendered)

    return {
        "status": "created",
        "project_name": project_name,
        "output_dir": str(target),
        "files_created": files_created,
        "warnings": warnings,
    }
