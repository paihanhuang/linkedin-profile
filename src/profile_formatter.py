"""Profile formatter: structure and format LinkedIn profile output."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


# LinkedIn character limits
LIMITS = {
    "headline": 220,
    "about": 2600,
    "experience_description": 2000,  # per role
    "skills_max": 50,  # max number of skills
}


def validate_section_length(section: str, content: str, limit: int) -> dict[str, Any]:
    """Validate that a profile section is within character limits.

    Returns:
        Dict with keys: section, char_count, limit, within_limit, overflow.
    """
    char_count = len(content)
    return {
        "section": section,
        "char_count": char_count,
        "limit": limit,
        "within_limit": char_count <= limit,
        "overflow": max(0, char_count - limit),
    }


def validate_profile(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate all profile sections against LinkedIn limits.

    Args:
        profile: Dict with keys matching section names (headline, about, etc.)

    Returns:
        List of validation results per section.
    """
    results = []

    if "headline" in profile:
        results.append(validate_section_length(
            "headline", profile["headline"], LIMITS["headline"]
        ))

    if "about" in profile:
        results.append(validate_section_length(
            "about", profile["about"], LIMITS["about"]
        ))

    if "experience" in profile:
        for i, exp in enumerate(profile["experience"]):
            desc = exp.get("description", "")
            results.append(validate_section_length(
                f"experience[{i}]", desc, LIMITS["experience_description"]
            ))

    if "skills" in profile:
        skill_count = len(profile["skills"])
        results.append({
            "section": "skills_count",
            "char_count": skill_count,
            "limit": LIMITS["skills_max"],
            "within_limit": skill_count <= LIMITS["skills_max"],
            "overflow": max(0, skill_count - LIMITS["skills_max"]),
        })

    return results


def format_profile_markdown(profile: dict[str, Any]) -> str:
    """Format a profile dict as a clean markdown document.

    Args:
        profile: Dict with keys: headline, about, experience, skills,
                 featured, education.

    Returns:
        Formatted markdown string.
    """
    lines = ["# LinkedIn Profile\n"]

    # Headline
    if "headline" in profile:
        lines.append(f"## Headline\n\n{profile['headline']}\n")
        lines.append(f"*({len(profile['headline'])} / {LIMITS['headline']} chars)*\n")

    # About
    if "about" in profile:
        lines.append(f"## About\n\n{profile['about']}\n")
        lines.append(f"*({len(profile['about'])} / {LIMITS['about']} chars)*\n")

    # Experience
    if "experience" in profile:
        lines.append("## Experience\n")
        for exp in profile["experience"]:
            title = exp.get("title", "")
            company = exp.get("company", "")
            dates = exp.get("dates", "")
            desc = exp.get("description", "")
            lines.append(f"### {title}")
            lines.append(f"**{company}** | {dates}\n")
            lines.append(f"{desc}\n")

    # Skills
    if "skills" in profile:
        lines.append("## Skills\n")
        for skill in profile["skills"]:
            lines.append(f"- {skill}")
        lines.append("")

    # Featured
    if "featured" in profile:
        lines.append("## Featured\n")
        for item in profile["featured"]:
            lines.append(f"- {item}")
        lines.append("")

    # Education
    if "education" in profile:
        lines.append("## Education\n")
        for edu in profile["education"]:
            lines.append(f"- {edu}")
        lines.append("")

    return "\n".join(lines)


def save_profile(content: str, output_dir: str | Path = "output") -> Path:
    """Save profile content to a timestamped markdown file.

    Args:
        content: Markdown content to save.
        output_dir: Directory for output files.

    Returns:
        Path to the saved file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"profile_{timestamp}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath
