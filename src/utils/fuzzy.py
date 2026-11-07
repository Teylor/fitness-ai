"""Búsqueda fuzzy de nombres."""

import unicodedata
from difflib import SequenceMatcher
from typing import Optional


def fuzzy_match(query: str, candidates: list[str], threshold: float = 0.6) -> Optional[str]:
    """Devuelve el candidato más parecido a query (difflib.SequenceMatcher.ratio).

    Args:
        query: Texto buscado.
        candidates: Lista de strings a comparar.
        threshold: Ratio mínimo [0..1] para aceptar un match (default 0.6).

    Returns:
        El candidato con el mayor ratio si es >= threshold, else None.
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
    """Normaliza un nombre: lowercase, sin acentos, sin espacios extra."""
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    return ' '.join(s.split())