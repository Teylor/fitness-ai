"""Tests: utils/fuzzy.py."""

from src.utils.fuzzy import fuzzy_match, normalize


def test_fuzzy_match_exact():
    candidates = ["huevo de pavo", "pan de pavo", "kiwi"]
    assert fuzzy_match("huevo de pavo", candidates) == "huevo de pavo"


def test_fuzzy_match_typo():
    candidates = ["huevo de pavo", "pan", "kiwi"]
    assert fuzzy_match("huevo de pav", candidates) == "huevo de pavo"


def test_fuzzy_match_no_match():
    candidates = ["huevo de pavo", "kiwi"]
    assert fuzzy_match("zzzz", candidates) is None


def test_normalize_accents():
    assert normalize("Ñandú") == "nandu"
    assert normalize("Café") == "cafe"


def test_normalize_case_and_spaces():
    assert normalize("  Huevo  DE   Pavo ") == "huevo de pavo"
