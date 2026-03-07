"""Tests for scaffold tool and template engine."""

import json
from pathlib import Path

import pytest

from src.template_engine import TemplateError, load_manifest, render_template, validate_no_unfilled
from src.tools.scaffold import scaffold_project

# Resolve the real templates dir relative to this test file
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


# --- Fixtures ---

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


# --- ML Project Tests ---

class TestScaffoldMLProject:
    def test_creates_all_expected_files(self, tmp_path):
        result = scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        assert result["status"] == "created"
        for f in EXPECTED_FILES:
            assert (tmp_path / f).exists(), f"Missing: {f}"

    def test_no_unfilled_placeholders(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "{{" not in claude_md
        assert "}}" not in claude_md

    def test_claude_md_contains_project_name(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "ml-pipeline" in claude_md

    def test_domain_constraints_present(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "Domain Constraints" in claude_md
        assert "reproducible via DVC" in claude_md

    def test_milestones_rendered(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "**M1:** Data ingestion" in claude_md
        assert "**M4:** Deployment" in claude_md

    def test_memory_files_have_agent_names(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        arch = (tmp_path / ".claude/agents/memory/architect-lessons.md").read_text()
        eng = (tmp_path / ".claude/agents/memory/engineer-lessons.md").read_text()
        qa = (tmp_path / ".claude/agents/memory/qa-lessons.md").read_text()
        assert "# Architect Lessons" in arch
        assert "# Engineer Lessons" in eng
        assert "# QA Lessons" in qa

    def test_settings_json_valid(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        settings = json.loads((tmp_path / ".claude/settings.json").read_text())
        assert "hooks" in settings


# --- Web Project Tests ---

class TestScaffoldWebProject:
    def test_creates_all_expected_files(self, tmp_path):
        result = scaffold_project(**WEB_PROJECT, output_dir=str(tmp_path))
        assert result["status"] == "created"
        for f in EXPECTED_FILES:
            assert (tmp_path / f).exists(), f"Missing: {f}"

    def test_domain_constraints_omitted_when_none(self, tmp_path):
        scaffold_project(**WEB_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "Domain Constraints" not in claude_md
        assert "None specified" not in claude_md

    def test_milestones_rendered(self, tmp_path):
        scaffold_project(**WEB_PROJECT, output_dir=str(tmp_path))
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "**M1:** Auth system" in claude_md
        assert "**M3:** Real-time updates" in claude_md

    def test_no_unfilled_placeholders_in_any_file(self, tmp_path):
        scaffold_project(**WEB_PROJECT, output_dir=str(tmp_path))
        for f in EXPECTED_FILES:
            content = (tmp_path / f).read_text()
            assert "{{" not in content, f"Unfilled placeholder in {f}"


# --- Template Validation Tests ---

class TestTemplateValidation:
    def test_unfilled_placeholder_raises(self):
        with pytest.raises(TemplateError, match="Unfilled placeholders"):
            validate_no_unfilled("Hello {{WORLD}}", "test.md")

    def test_all_filled_passes(self):
        validate_no_unfilled("Hello world", "test.md")

    def test_conditional_removed_when_empty(self):
        template = "before\n{{#IF OPT}}optional content{{/IF OPT}}\nafter"
        result = render_template(template, {"OPT": ""}, "test.md")
        assert "optional content" not in result
        assert "before" in result
        assert "after" in result

    def test_conditional_kept_when_filled(self):
        template = "before\n{{#IF OPT}}\noptional: {{OPT}}\n{{/IF OPT}}\nafter"
        result = render_template(template, {"OPT": "value"}, "test.md")
        assert "optional: value" in result

    def test_conditional_removed_when_missing_key(self):
        template = "before\n{{#IF MISSING}}content{{/IF MISSING}}\nafter"
        result = render_template(template, {}, "test.md")
        assert "content" not in result

    def test_conditional_removed_when_whitespace_only(self):
        template = "before\n{{#IF OPT}}content{{/IF OPT}}\nafter"
        result = render_template(template, {"OPT": "   "}, "test.md")
        assert "content" not in result

    def test_no_excessive_blank_lines_after_removal(self):
        template = "before\n\n{{#IF OPT}}\ncontent\n{{/IF OPT}}\n\nafter"
        result = render_template(template, {"OPT": ""}, "test.md")
        assert "\n\n\n" not in result

    def test_render_vars_override_globals(self):
        template = "Agent: {{AGENT_NAME}}"
        result = render_template(template, {"AGENT_NAME": "Architect"}, "test.md")
        assert result == "Agent: Architect"


# --- Manifest Validation Tests ---

class TestManifestValidation:
    def test_valid_manifest_loads(self):
        manifest = load_manifest(TEMPLATES_DIR)
        assert "templates" in manifest
        assert len(manifest["templates"]) > 0

    def test_all_source_files_exist(self):
        manifest = load_manifest(TEMPLATES_DIR)
        for entry in manifest["templates"]:
            source = TEMPLATES_DIR / entry["source"]
            assert source.exists(), f"Missing: {entry['source']}"

    def test_missing_manifest_raises(self, tmp_path):
        with pytest.raises(TemplateError, match="Manifest not found"):
            load_manifest(tmp_path)

    def test_malformed_json_raises(self, tmp_path):
        (tmp_path / "manifest.json").write_text("not json{", encoding="utf-8")
        with pytest.raises(TemplateError, match="Malformed manifest JSON"):
            load_manifest(tmp_path)

    def test_missing_source_file_raises(self, tmp_path):
        manifest = {
            "version": 1,
            "templates": [
                {"id": "test", "source": "nonexistent.md", "output": "out.md", "mode": "copy"}
            ],
        }
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(TemplateError, match="Template source not found"):
            load_manifest(tmp_path)

    def test_unknown_mode_raises(self, tmp_path):
        (tmp_path / "test.md").write_text("content", encoding="utf-8")
        manifest = {
            "version": 1,
            "templates": [
                {"id": "test", "source": "test.md", "output": "out.md", "mode": "unknown"}
            ],
        }
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(TemplateError, match="Unknown mode"):
            load_manifest(tmp_path)


# --- Edge Cases ---

class TestScaffoldEdgeCases:
    def test_force_overwrites(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        result = scaffold_project(**ML_PROJECT, output_dir=str(tmp_path), force=True)
        assert result["status"] == "created"
        assert len(result["warnings"]) == 0
        assert len(result["files_created"]) == len(EXPECTED_FILES)

    def test_no_force_skips_existing(self, tmp_path):
        scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        result = scaffold_project(**ML_PROJECT, output_dir=str(tmp_path), force=False)
        assert result["status"] == "created"
        assert len(result["files_created"]) == 0
        assert len(result["warnings"]) == len(EXPECTED_FILES)
        assert all("Skipped" in w for w in result["warnings"])

    def test_invalid_project_name(self):
        result = scaffold_project(
            project_name="My Project",
            description="test",
            tech_stack="test",
            milestones=["m1"],
        )
        assert "error" in result
        assert "project_name" in result["details"]

    def test_empty_milestones(self):
        result = scaffold_project(
            project_name="test",
            description="test",
            tech_stack="test",
            milestones=[],
        )
        assert "error" in result
        assert result["details"]["field"] == "milestones"

    def test_return_shape(self, tmp_path):
        result = scaffold_project(**ML_PROJECT, output_dir=str(tmp_path))
        assert set(result.keys()) == {"status", "project_name", "output_dir", "files_created", "warnings"}

    def test_missing_manifest_returns_error(self, tmp_path, monkeypatch):
        # Point templates dir to an empty directory
        empty_templates = tmp_path / "empty_templates"
        empty_templates.mkdir()
        monkeypatch.setattr("src.tools.scaffold.resolve_templates_dir", lambda: empty_templates)
        result = scaffold_project(**ML_PROJECT, output_dir=str(tmp_path / "out"))
        assert "error" in result
        assert "Manifest" in result["error"]
