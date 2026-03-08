"""Message Batches API tools — submit, check, and retrieve batch results for 50% cost savings."""

import logging
import os

import anthropic

from src.config import DEFAULT_BATCH_MODEL, DEFAULT_BATCH_MAX_TOKENS

logger = logging.getLogger(__name__)


def _get_client() -> anthropic.Anthropic:
    """Get an Anthropic client. Requires ANTHROPIC_API_KEY env var."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)


def submit_batch(
    tasks: list[dict],
    model: str | None = None,
    max_tokens: int | None = None,
) -> dict:
    """Submit prompts to the Message Batches API for 50% cost savings.

    Use for non-urgent tasks that don't need immediate responses (results
    typically ready within minutes, guaranteed within 24 hours).

    Each task dict needs:
    - id: unique string identifier for the task
    - prompt: the user message to send
    - system: optional system prompt string

    model: Claude model to use (default: claude-sonnet-4-20250514)
    max_tokens: max response tokens per task (default: 4096)

    Returns batch_id for tracking. Use check_batch() to poll status
    and get_batch_results() to retrieve completed results.
    """
    logger.info("submit_batch: %d tasks", len(tasks))

    if not isinstance(tasks, list) or len(tasks) == 0:
        return {"error": "Tasks must be a non-empty list",
                "details": {"field": "tasks"}}

    model = model or DEFAULT_BATCH_MODEL
    max_tokens = max_tokens or DEFAULT_BATCH_MAX_TOKENS

    # Validate and build requests
    requests = []
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            return {"error": f"Task at index {i} must be a dict",
                    "details": {"index": i}}

        task_id = task.get("id")
        prompt = task.get("prompt")

        if not task_id or not isinstance(task_id, str):
            return {"error": f"Task at index {i} missing 'id' (string)",
                    "details": {"index": i}}
        if not prompt or not isinstance(prompt, str):
            return {"error": f"Task at index {i} missing 'prompt' (string)",
                    "details": {"index": i}}

        params: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        system = task.get("system")
        if system and isinstance(system, str):
            params["system"] = system

        requests.append({
            "custom_id": task_id,
            "params": params,
        })

    try:
        client = _get_client()
        batch = client.messages.batches.create(requests=requests)
        return {
            "status": "submitted",
            "batch_id": batch.id,
            "processing_status": batch.processing_status,
            "task_count": len(requests),
        }
    except ValueError as e:
        return {"error": str(e), "details": {"type": "config_error"}}
    except anthropic.APIError as e:
        return {"error": f"API error: {e.message}", "details": {"type": "api_error"}}


def check_batch(batch_id: str) -> dict:
    """Check the status of a submitted batch.

    Returns processing status and request counts (succeeded, errored,
    expired, processing, canceled).
    """
    logger.info("check_batch: batch_id=%s", batch_id)

    if not batch_id or not isinstance(batch_id, str):
        return {"error": "batch_id must be a non-empty string"}

    try:
        client = _get_client()
        batch = client.messages.batches.retrieve(batch_id)
        return {
            "batch_id": batch.id,
            "processing_status": batch.processing_status,
            "counts": {
                "succeeded": batch.request_counts.succeeded,
                "errored": batch.request_counts.errored,
                "expired": batch.request_counts.expired,
                "processing": batch.request_counts.processing,
                "canceled": batch.request_counts.canceled,
            },
        }
    except ValueError as e:
        return {"error": str(e), "details": {"type": "config_error"}}
    except anthropic.APIError as e:
        return {"error": f"API error: {e.message}", "details": {"type": "api_error"}}


def get_batch_results(batch_id: str) -> dict:
    """Retrieve results from a completed batch.

    Returns a list of results, each with: custom_id, status, and content
    (the response text for succeeded requests).
    """
    logger.info("get_batch_results: batch_id=%s", batch_id)

    if not batch_id or not isinstance(batch_id, str):
        return {"error": "batch_id must be a non-empty string"}

    try:
        client = _get_client()

        # Check if batch is done first
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status != "ended":
            return {
                "batch_id": batch_id,
                "processing_status": batch.processing_status,
                "results": [],
                "message": "Batch is still processing. Check again later.",
            }

        results = []
        for entry in client.messages.batches.results(batch_id):
            result_entry = {
                "custom_id": entry.custom_id,
                "status": entry.result.type,
            }
            if entry.result.type == "succeeded":
                # Extract text from content blocks
                texts = []
                for block in entry.result.message.content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                result_entry["content"] = "\n".join(texts)
            elif entry.result.type == "errored":
                result_entry["error"] = str(entry.result.error)

            results.append(result_entry)

        return {
            "batch_id": batch_id,
            "processing_status": "ended",
            "results": results,
        }
    except ValueError as e:
        return {"error": str(e), "details": {"type": "config_error"}}
    except anthropic.APIError as e:
        return {"error": f"API error: {e.message}", "details": {"type": "api_error"}}
