"""Búsqueda fuzzy de nombres."""

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
    ...