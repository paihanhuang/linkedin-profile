"""Scoring utilities: keyword overlap and job posting match scoring."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


def normalize_keyword(keyword: str) -> str:
    """Normalize a keyword for matching (lowercase, strip whitespace)."""
    return keyword.strip().lower()


def extract_keywords_from_text(text: str, keyword_list: list[str]) -> dict[str, bool]:
    """Check which keywords from a list appear in the given text.

    Args:
        text: The text to search (e.g., a profile or job posting).
        keyword_list: List of keywords to look for.

    Returns:
        Dict mapping each keyword to True (found) or False (not found).
    """
    text_lower = text.lower()
    results = {}
    for kw in keyword_list:
        normalized = normalize_keyword(kw)
        results[kw] = normalized in text_lower
    return results


def calculate_overlap_score(
    profile_text: str,
    posting_text: str,
    target_keywords: list[str] | None = None,
) -> dict[str, Any]:
    """Calculate keyword overlap between a profile and a job posting.

    Args:
        profile_text: The generated LinkedIn profile text.
        posting_text: A job posting's text content.
        target_keywords: Optional explicit list of keywords to check.
            If None, extracts common multi-word phrases from the posting.

    Returns:
        Dict with: matched, missed, overlap_percentage, total_keywords.
    """
    if target_keywords is None:
        # Extract significant words from posting (simple approach)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', posting_text.lower())
        word_freq = Counter(words)
        # Take top 30 most frequent words, excluding common stop words
        stop_words = {
            "the", "and", "for", "with", "that", "this", "from", "are",
            "will", "have", "been", "has", "was", "our", "you", "your",
            "can", "not", "but", "all", "also", "may", "more", "than",
            "into", "about", "other", "which", "their", "what", "when",
            "who", "how", "its", "any", "each", "would", "should",
            "could", "being", "these", "those", "such",
        }
        target_keywords = [
            word for word, _ in word_freq.most_common(60)
            if word not in stop_words
        ][:30]

    profile_lower = profile_text.lower()
    matched = [kw for kw in target_keywords if normalize_keyword(kw) in profile_lower]
    missed = [kw for kw in target_keywords if normalize_keyword(kw) not in profile_lower]

    total = len(target_keywords)
    overlap_pct = (len(matched) / total * 100) if total > 0 else 0.0

    return {
        "matched": matched,
        "missed": missed,
        "overlap_percentage": round(overlap_pct, 1),
        "total_keywords": total,
        "matched_count": len(matched),
        "missed_count": len(missed),
    }


def score_against_postings(
    profile_text: str,
    postings: list[dict[str, str]],
    target_keywords: list[str] | None = None,
) -> dict[str, Any]:
    """Score a profile against multiple job postings.

    Args:
        profile_text: The generated LinkedIn profile text.
        postings: List of dicts with keys: title, source, text.
        target_keywords: Optional keyword list for all postings.

    Returns:
        Dict with per-posting scores and aggregate score.
    """
    results = []
    for posting in postings:
        score = calculate_overlap_score(
            profile_text,
            posting.get("text", ""),
            target_keywords,
        )
        results.append({
            "title": posting.get("title", "Unknown"),
            "source": posting.get("source", "Unknown"),
            **score,
        })

    if results:
        avg_overlap = sum(r["overlap_percentage"] for r in results) / len(results)
    else:
        avg_overlap = 0.0

    return {
        "per_posting": results,
        "aggregate_overlap_percentage": round(avg_overlap, 1),
        "postings_analyzed": len(results),
    }
