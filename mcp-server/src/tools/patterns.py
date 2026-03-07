"""Pattern storage tools — save, retrieve, search, and delete reusable code patterns."""

import fcntl
import json
import logging
import os
import re
import tempfile
from pathlib import Path

from src.config import STORE_DIR, STORE_FILE, STORE_VERSION

logger = logging.getLogger(__name__)

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _read_store() -> list[dict]:
    """Read patterns from the store file. Returns [] if file doesn't exist."""
    if not STORE_FILE.exists():
        return []
    try:
        data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        return data.get("patterns", [])
    except json.JSONDecodeError as e:
        logger.error("Corrupt patterns.json: %s", e)
        return []


def _write_store(patterns: list[dict]) -> None:
    """Atomically write patterns to the store file with file locking."""
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    data = {"version": STORE_VERSION, "patterns": patterns}
    content = json.dumps(data, indent=2, ensure_ascii=False)

    # Atomic write: write to tmpfile in same dir, then rename
    fd, tmp_path = tempfile.mkstemp(dir=str(STORE_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp_path, str(STORE_FILE))
    except Exception:
        # Clean up tmpfile on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def save_pattern(
    name: str,
    description: str,
    code: str,
    language: str,
    tags: list[str],
) -> dict:
    """Save a reusable code pattern. Upserts if name already exists.

    All fields are required and must be non-empty strings (tags must be a non-empty list).
    Name must match ^[a-z0-9][a-z0-9-]*$.
    """
    logger.info("save_pattern: name=%s", name)

    # Validate required fields — empty strings treated as missing
    for field_name, value in [("name", name), ("description", description),
                               ("code", code), ("language", language)]:
        if not isinstance(value, str) or not value.strip():
            return {"error": f"Missing or empty field: {field_name}",
                    "details": {"field": field_name}}

    if not isinstance(tags, list) or len(tags) == 0:
        return {"error": "Missing or empty field: tags",
                "details": {"field": "tags"}}

    for i, tag in enumerate(tags):
        if not isinstance(tag, str) or not tag.strip():
            return {"error": f"Invalid tag at index {i}: must be non-empty string",
                    "details": {"field": "tags", "index": i}}

    if not NAME_PATTERN.match(name):
        return {"error": "Invalid name: must match ^[a-z0-9][a-z0-9-]*$",
                "details": {"name": name}}

    patterns = _read_store()

    # Upsert: replace if exists
    new_pattern = {
        "name": name,
        "description": description,
        "code": code,
        "language": language,
        "tags": tags,
    }
    replaced = False
    for i, p in enumerate(patterns):
        if p.get("name") == name:
            patterns[i] = new_pattern
            replaced = True
            break
    if not replaced:
        patterns.append(new_pattern)

    _write_store(patterns)
    return {"status": "saved", "name": name, "total_patterns": len(patterns)}


def get_pattern(name: str) -> dict:
    """Retrieve a pattern by exact name."""
    logger.info("get_pattern: name=%s", name)
    patterns = _read_store()
    for p in patterns:
        if p.get("name") == name:
            return p
    return {"error": "Pattern not found", "details": {"name": name}}


def search_patterns(
    query: str | None = None,
    language: str | None = None,
    tag: str | None = None,
) -> list[dict]:
    """Search patterns with AND filtering across filter types.

    query: case-insensitive substring match on name OR description.
    language: exact match, case-insensitive.
    tag: any pattern tag matches, case-insensitive.
    Multiple filter types are ANDed. All None returns all patterns. Returns [] if no matches.
    """
    logger.info("search_patterns: query=%s, language=%s, tag=%s", query, language, tag)
    patterns = _read_store()
    results = []

    for p in patterns:
        # query filter: substring match on name OR description
        if query is not None:
            q = query.lower()
            if q not in p.get("name", "").lower() and q not in p.get("description", "").lower():
                continue

        # language filter: exact match, case-insensitive
        if language is not None:
            if p.get("language", "").lower() != language.lower():
                continue

        # tag filter: any tag matches
        if tag is not None:
            pattern_tags = [t.lower() for t in p.get("tags", [])]
            if tag.lower() not in pattern_tags:
                continue

        results.append(p)

    results.sort(key=lambda x: x.get("name", ""))
    return results


def delete_pattern(name: str) -> dict:
    """Delete a pattern by exact name."""
    logger.info("delete_pattern: name=%s", name)
    patterns = _read_store()
    new_patterns = [p for p in patterns if p.get("name") != name]

    if len(new_patterns) == len(patterns):
        return {"error": "Pattern not found", "details": {"name": name}}

    _write_store(new_patterns)
    return {"status": "deleted", "name": name}
