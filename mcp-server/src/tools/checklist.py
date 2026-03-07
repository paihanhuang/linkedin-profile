"""Checklist verification tool — run shell-based acceptance criteria checks."""

import asyncio
import logging
import os
import signal
import time
from pathlib import Path

from src.config import DEFAULT_CHECK_TIMEOUT, MAX_CHECK_TIMEOUT, MAX_EVIDENCE_CHARS

logger = logging.getLogger(__name__)


def _truncate_evidence(text: str) -> str:
    """Truncate evidence to MAX_EVIDENCE_CHARS, appending [truncated] if needed."""
    if len(text) <= MAX_EVIDENCE_CHARS:
        return text
    return text[:MAX_EVIDENCE_CHARS] + "[truncated]"


async def check_criteria(
    criteria: list[dict],
    working_dir: str | None = None,
) -> dict:
    """Run shell-based acceptance criteria checks and report results.

    Each criterion has: description (str), check (str — shell command),
    and optional timeout (int — seconds).
    Exit 0 = pass, non-zero = fail. Timeouts and exceptions produce
    their own status values.
    """
    logger.info("check_criteria: %d criteria, working_dir=%s", len(criteria), working_dir)

    # Resolve working directory
    cwd = Path(working_dir) if working_dir else Path.cwd()
    if not cwd.exists():
        return {"error": "Working directory does not exist",
                "details": {"working_dir": str(cwd)}}

    # Empty criteria list
    if len(criteria) == 0:
        return {
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0, "timeouts": 0},
            "results": [],
        }

    results = []
    counts = {"passed": 0, "failed": 0, "errors": 0, "timeouts": 0}

    for criterion in criteria:
        description = criterion.get("description", "")
        check_cmd = criterion.get("check", "")
        timeout_val = criterion.get("timeout", DEFAULT_CHECK_TIMEOUT)

        # Cap timeout
        if timeout_val is None:
            timeout_val = DEFAULT_CHECK_TIMEOUT
        timeout_val = min(max(1, timeout_val), MAX_CHECK_TIMEOUT)

        start_time = time.monotonic()
        result_entry: dict = {"description": description, "check": check_cmd}

        try:
            proc = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),
                start_new_session=True,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout_val
                )
            except asyncio.TimeoutError:
                # Kill the entire process group to clean up child processes
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
                try:
                    await proc.wait()
                except Exception:
                    pass
                elapsed = time.monotonic() - start_time
                result_entry["status"] = "timeout"
                result_entry["evidence"] = _truncate_evidence(
                    f"Command timed out after {timeout_val}s"
                )
                result_entry["duration_ms"] = max(0, int(elapsed * 1000))
                counts["timeouts"] += 1
                results.append(result_entry)
                continue

            elapsed = time.monotonic() - start_time
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")

            evidence = stdout
            if stderr.strip():
                evidence = stdout + "\n[stderr] " + stderr

            if proc.returncode == 0:
                result_entry["status"] = "pass"
                result_entry["evidence"] = _truncate_evidence(stdout)
                counts["passed"] += 1
            elif proc.returncode in (126, 127):
                # 126 = permission denied, 127 = command not found
                result_entry["status"] = "error"
                result_entry["evidence"] = _truncate_evidence(evidence)
                counts["errors"] += 1
            else:
                result_entry["status"] = "fail"
                result_entry["evidence"] = _truncate_evidence(evidence)
                counts["failed"] += 1

            result_entry["duration_ms"] = max(0, int(elapsed * 1000))

        except Exception as e:
            elapsed = time.monotonic() - start_time
            result_entry["status"] = "error"
            result_entry["evidence"] = _truncate_evidence(str(e))
            result_entry["duration_ms"] = max(0, int(elapsed * 1000))
            counts["errors"] += 1

        results.append(result_entry)

    return {
        "summary": {
            "total": len(results),
            "passed": counts["passed"],
            "failed": counts["failed"],
            "errors": counts["errors"],
            "timeouts": counts["timeouts"],
        },
        "results": results,
    }
