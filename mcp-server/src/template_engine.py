"""Template engine — render, validate, and manage scaffold templates."""

import json
import re
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")
CONDITIONAL_RE = re.compile(r"\{\{#IF (\w+)\}\}(.*?)\{\{/IF \1\}\}", re.DOTALL)


class TemplateError(Exception):
    """Raised when template rendering or validation fails."""


def _process_conditionals(template: str, placeholder_map: dict[str, str]) -> str:
    """Remove conditional blocks whose placeholder value is empty/missing.

    Syntax: {{#IF KEY}}...content...{{/IF KEY}}
    If KEY is missing, None, empty string, or whitespace-only, the entire block
    (including tags) is removed. Otherwise tags are stripped and content is kept.

    No nesting supported. Unmatched tags are left as-is (caught by validation).
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        value = placeholder_map.get(key, "")
        if not value or not value.strip():
            return ""
        return match.group(2)

    return CONDITIONAL_RE.sub(_replace, template)


def _collapse_blank_lines(text: str) -> str:
    """Collapse runs of 3+ blank lines to 2 (one visual blank line between sections)."""
    return re.sub(r"\n{3,}", "\n\n", text)


def render_template(
    template_content: str,
    placeholder_map: dict[str, str],
    source_name: str = "<unknown>",
) -> str:
    """Render a template: process conditionals, replace placeholders, validate.

    Steps:
    1. Process {{#IF ...}} conditional blocks (before substitution)
    2. Single-pass {{PLACEHOLDER}} replacement
    3. Collapse excessive blank lines
    4. Validate no unfilled placeholders remain

    Raises TemplateError if unfilled placeholders remain.
    """
    # Step 1: conditionals (evaluated against raw map, before substitution)
    result = _process_conditionals(template_content, placeholder_map)

    # Step 2: single-pass placeholder replacement
    def _replace_placeholder(match: re.Match) -> str:
        key = match.group(1)
        return placeholder_map.get(key, match.group(0))

    result = PLACEHOLDER_RE.sub(_replace_placeholder, result)

    # Step 3: collapse blank lines
    result = _collapse_blank_lines(result)

    # Step 4: validate
    validate_no_unfilled(result, source_name)

    return result


def validate_no_unfilled(rendered: str, source_name: str) -> None:
    """Check that no {{PLACEHOLDER}} tokens remain in rendered output.

    Raises TemplateError listing the unfilled placeholders and source file.
    """
    remaining = PLACEHOLDER_RE.findall(rendered)
    if remaining:
        unique = sorted(set(remaining))
        raise TemplateError(
            f"Unfilled placeholders in {source_name}: {unique}"
        )


def load_manifest(templates_dir: Path) -> dict:
    """Load and validate manifest.json from templates directory.

    Validates:
    - File exists and is valid JSON
    - Has 'version' and 'templates' keys
    - Each entry has required fields: id, source, output, mode
    - Mode is one of: copy, render
    - All source files exist on disk

    Returns the manifest dict. Raises TemplateError on any issue.
    """
    manifest_path = templates_dir / "manifest.json"
    if not manifest_path.exists():
        raise TemplateError(f"Manifest not found: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise TemplateError(f"Malformed manifest JSON: {e}") from e

    if "templates" not in manifest:
        raise TemplateError("Manifest missing 'templates' key")

    valid_modes = {"copy", "render"}
    for entry in manifest["templates"]:
        for field in ("id", "source", "output", "mode"):
            if field not in entry:
                raise TemplateError(
                    f"Manifest entry missing '{field}': {entry}"
                )
        if entry["mode"] not in valid_modes:
            raise TemplateError(
                f"Unknown mode '{entry['mode']}' in entry '{entry['id']}'"
            )
        source_path = templates_dir / entry["source"]
        if not source_path.exists():
            raise TemplateError(
                f"Template source not found: {entry['source']} "
                f"(entry '{entry['id']}')"
            )

    return manifest
