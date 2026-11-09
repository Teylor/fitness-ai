"""Fuzzy matching utilities for names."""

import unicodedata
from difflib import SequenceMatcher
from typing import Optional


def fuzzy_match(query: str, candidates: list[str], threshold: float = 0.6) -> Optional[str]:
    """Return the candidate closest to query (difflib.SequenceMatcher.ratio).

    Args:
        query: Search string.
        candidates: List of strings to compare against.
        threshold: Minimum ratio [0..1] to accept a match (default 0.6).

    Returns:
        The candidate with the highest ratio if >= threshold, else None.
    """
    if not candidates:
        return None
    q = normalize(query)
    best = None
    best_ratio = 0.0
    for cand in candidates:
        ratio = SequenceMatcher(None, q, normalize(cand)).ratio()
        if ratio > best_ratio:
            best = cand
            best_ratio = ratio
    return best if best_ratio >= threshold else None


def normalize(name: str) -> str:
    """Normalize a name: lowercase, strip accents, collapse extra whitespace."""
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    return ' '.join(s.split())
