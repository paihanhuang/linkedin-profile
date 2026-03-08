"""Centralized constants and configuration for claude-mcp-server."""

import os
from pathlib import Path

# Pattern store
STORE_DIR: Path = Path(os.environ.get("CLAUDE_MCP_STORE_DIR", str(Path.home() / ".claude-mcp")))
STORE_FILE: Path = STORE_DIR / "patterns.json"
STORE_VERSION: int = 1

# Templates
TEMPLATES_DIR_ENV: str = "CLAUDE_MCP_TEMPLATES_DIR"

# Checklist
DEFAULT_CHECK_TIMEOUT: int = 30
MAX_CHECK_TIMEOUT: int = 300
MAX_EVIDENCE_CHARS: int = 5000

# Batch API
DEFAULT_BATCH_MODEL: str = "claude-sonnet-4-20250514"
DEFAULT_BATCH_MAX_TOKENS: int = 4096


def resolve_templates_dir() -> Path | None:
    """Resolve the templates directory.

    Priority:
    1. CLAUDE_MCP_TEMPLATES_DIR environment variable
    2. Walk up from this file looking for a directory containing
       both CLAUDE.md and templates/ (dev fallback)
    """
    env_val = os.environ.get(TEMPLATES_DIR_ENV)
    if env_val:
        p = Path(env_val)
        if p.is_dir():
            return p
        return None

    # Dev fallback: walk up from __file__ looking for project root
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "templates"
        if candidate.is_dir() and (current / "CLAUDE.md").exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None
