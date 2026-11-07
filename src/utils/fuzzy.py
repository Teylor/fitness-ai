"""Búsqueda fuzzy de nombres."""

import unicodedata
from typing import Optional


def fuzzy_match(query: str, candidates: list[str]) -> Optional[str]:
    """Devuelve el candidato más parecido a query (Levenshtein / token sort).

    Args:
        query: Texto buscado.
        candidates: Lista de strings a comparar.

    Returns:
        El match más cercano o None si no hay coincidencia aceptable.
    """
    ...


def normalize(name: str) -> str:
    """Normaliza un nombre: lowercase, sin acentos, sin espacios extra."""
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    return ' '.join(s.split())