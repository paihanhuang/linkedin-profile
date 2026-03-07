"""Cross-project validation tests — verify scaffold works across project types."""

import json

import pytest

from src.tools.scaffold import scaffold_project

# --- 4 Project Type Fixtures ---

ML_PROJECT = {
    "project_name": "ml-pipeline",
    "description": "An ML training and inference pipeline for tabular data",
    "tech_stack": "Python 3.11, PyTorch, pandas, DVC",
    "milestones": ["Data ingestion", "Model training", "Evaluation", "Deployment"],
    "domain_constraints": ["Models must be reproducible via DVC", "No GPU required for tests"],
}

WEB_PROJECT = {
    "project_name": "web-dashboard",
    "description": "A real-time analytics dashboard for e-commerce metrics",
    "tech_stack": "TypeScript, React, Next.js, PostgreSQL",
    "milestones": ["Auth system", "Dashboard views", "Real-time updates"],
    "domain_constraints": None,
}

CLI_PROJECT = {
    "project_name": "cli-tool",
    "description": "A command-line tool for database migration management",
    "tech_stack": "Rust, clap, SQLx",
    "milestones": ["Parse migration files", "Apply migrations", "Rollback support", "Status command"],
    "domain_constraints": ["Must support PostgreSQL and SQLite", "Zero-downtime migrations required"],
}

DATA_PIPELINE_PROJECT = {
    "project_name": "data-pipeline",
    "description": "A batch data processing pipeline for ETL workflows",
    "tech_stack": "Python 3.11, Apache Beam, BigQuery, Airflow",
    "milestones": ["Data extraction", "Transform logic", "BigQuery loading", "Scheduling"],
    "domain_constraints": ["Must process 10M+ rows per batch", "Idempotent transformations"],
}

ALL_PROJECTS = [ML_PROJECT, WEB_PROJECT, CLI_PROJECT, DATA_PIPELINE_PROJECT]
PROJECT_IDS = ["ml", "web", "cli", "data-pipeline"]

EXPECTED_FILES = [
    "CLAUDE.md",
    ".claude/agents/architect.md",
    ".claude/agents/engineer.md",
    ".claude/agents/qa.md",
    ".claude/agents/memory/architect-lessons.md",
    ".claude/agents/memory/engineer-lessons.md",
    ".claude/agents/memory/qa-lessons.md",
    ".claude/skills/pipeline/SKILL.md",
    ".claude/skills/critique/SKILL.md",
    ".claude/hooks/guard-protected-files.sh",
    ".claude/hooks/memory-reminder.sh",
    ".claude/settings.json",
]


# --- Cross-Project File Structure Tests ---

class TestCrossProjectFileStructure:
    @pytest.fixture(params=ALL_PROJECTS, ids=PROJECT_IDS)
    def scaffolded(self, request, tmp_path):
        result = scaffold_project(**request.param, output_dir=str(tmp_path))
        return result, tmp_path, request.param

    def test_scaffold_succeeds(self, scaffolded):
        result, _, _ = scaffolded
        assert result["status"] == "created"

    def test_all_expected_files_exist(self, scaffolded):
        _, path, _ = scaffolded
        for f in EXPECTED_FILES:
            assert (path / f).exists(), f"Missing: {f}"

    def test_no_unfilled_placeholders(self, scaffolded):
        _, path, _ = scaffolded
        for f in EXPECTED_FILES:
            content = (path / f).read_text()
            assert "{{" not in content, f"Unfilled placeholder in {f}"

    def test_claude_md_contains_project_name(self, scaffolded):
        _, path, params = scaffolded
        claude_md = (path / "CLAUDE.md").read_text()
        assert params["project_name"] in claude_md

    def test_claude_md_contains_tech_stack(self, scaffolded):
        _, path, params = scaffolded
        claude_md = (path / "CLAUDE.md").read_text()
        assert params["tech_stack"] in claude_md

    def test_milestones_all_present(self, scaffolded):
        _, path, params = scaffolded
        claude_md = (path / "CLAUDE.md").read_text()
        for i, m in enumerate(params["milestones"]):
            assert f"**M{i+1}:** {m}" in claude_md

    def test_domain_constraints_present_when_provided(self, scaffolded):
        _, path, params = scaffolded
        if params.get("domain_constraints"):
            claude_md = (path / "CLAUDE.md").read_text()
            assert "Domain Constraints" in claude_md
            for c in params["domain_constraints"]:
                assert c in claude_md

    def test_domain_constraints_absent_when_none(self, scaffolded):
        _, path, params = scaffolded
        if params.get("domain_constraints") is None:
            claude_md = (path / "CLAUDE.md").read_text()
            assert "Domain Constraints" not in claude_md


# --- Structural Integrity Tests ---

class TestCrossProjectStructuralIntegrity:
    @pytest.fixture(params=ALL_PROJECTS, ids=PROJECT_IDS)
    def project_path(self, request, tmp_path):
        scaffold_project(**request.param, output_dir=str(tmp_path))
        return tmp_path

    def test_settings_json_valid(self, project_path):
        settings = json.loads((project_path / ".claude/settings.json").read_text())
        assert "hooks" in settings

    def test_settings_hooks_reference_existing_scripts(self, project_path):
        settings = json.loads((project_path / ".claude/settings.json").read_text())
        for event, entries in settings.get("hooks", {}).items():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    cmd = hook.get("command", "")
                    parts = cmd.split()
                    if len(parts) >= 2 and parts[0] == "bash":
                        script = parts[1]
                        assert (project_path / script).exists(), f"Hook script missing: {script}"

    def test_agent_templates_have_required_sections(self, project_path):
        for agent in ["architect", "engineer", "qa"]:
            content = (project_path / f".claude/agents/{agent}.md").read_text()
            assert "## Context" in content or "## Role" in content
            assert "## Hard Rules" in content or "## Output" in content

    def test_memory_files_have_correct_agent_names(self, project_path):
        for agent, name in [("architect", "Architect"), ("engineer", "Engineer"), ("qa", "QA")]:
            content = (project_path / f".claude/agents/memory/{agent}-lessons.md").read_text()
            assert f"# {name} Lessons" in content

    def test_pipeline_skill_has_frontmatter(self, project_path):
        content = (project_path / ".claude/skills/pipeline/SKILL.md").read_text()
        assert content.startswith("---")
        assert "name: pipeline" in content

    def test_critique_skill_has_frontmatter(self, project_path):
        content = (project_path / ".claude/skills/critique/SKILL.md").read_text()
        assert content.startswith("---")
        assert "name: critique" in content

    def test_claude_md_under_80_lines(self, project_path):
        claude_md = (project_path / "CLAUDE.md").read_text()
        line_count = len(claude_md.splitlines())
        assert line_count <= 80, f"CLAUDE.md is {line_count} lines, should be <= 80"

    def test_claude_md_has_required_sections(self, project_path):
        claude_md = (project_path / "CLAUDE.md").read_text()
        assert "## Project" in claude_md
        assert "## Tech Stack" in claude_md
        assert "## Milestones" in claude_md
        assert "## Project Structure" in claude_md

    def test_hook_scripts_have_shebang(self, project_path):
        for hook_file in (project_path / ".claude/hooks").iterdir():
            if hook_file.suffix == ".sh":
                content = hook_file.read_text()
                assert content.startswith("#!/"), f"Missing shebang in {hook_file.name}"


# --- Edge Cases ---

class TestCrossProjectEdgeCases:
    def test_single_milestone(self, tmp_path):
        result = scaffold_project(
            project_name="tiny-project",
            description="A minimal project with one milestone",
            tech_stack="Python 3.11",
            milestones=["Complete everything"],
            output_dir=str(tmp_path),
        )
        assert result["status"] == "created"
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "**M1:** Complete everything" in claude_md

    def test_many_milestones(self, tmp_path):
        result = scaffold_project(
            project_name="big-project",
            description="A project with many milestones",
            tech_stack="Go, gRPC, Kubernetes",
            milestones=[f"Phase {i}" for i in range(1, 11)],
            output_dir=str(tmp_path),
        )
        assert result["status"] == "created"
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "**M10:** Phase 10" in claude_md

    def test_empty_constraints_list(self, tmp_path):
        result = scaffold_project(
            project_name="empty-constraints",
            description="A project with empty constraints list",
            tech_stack="Rust",
            milestones=["Build it"],
            domain_constraints=[],
            output_dir=str(tmp_path),
        )
        assert result["status"] == "created"
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "Domain Constraints" not in claude_md

    def test_long_description(self, tmp_path):
        long_desc = "A comprehensive platform for managing distributed systems " * 10
        result = scaffold_project(
            project_name="verbose-project",
            description=long_desc.strip(),
            tech_stack="Java 21, Spring Boot",
            milestones=["Setup", "Core", "Deploy"],
            output_dir=str(tmp_path),
        )
        assert result["status"] == "created"
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "{{" not in claude_md

    def test_special_chars_in_tech_stack(self, tmp_path):
        result = scaffold_project(
            project_name="special-project",
            description="A project with special chars in tech stack",
            tech_stack="C++, C#, F#, Node.js >= 20",
            milestones=["Build"],
            output_dir=str(tmp_path),
        )
        assert result["status"] == "created"
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "C++" in claude_md
        assert "Node.js >= 20" in claude_md
