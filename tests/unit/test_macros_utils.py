"""Tests: utils/macros.py."""

from types import SimpleNamespace

from src.utils.macros import (
    calc_ingredient_macros,
    calc_recipe_macros,
    estimate_1rm,
)


def test_calc_ingredient_macros_gr():
    ing = SimpleNamespace(unit="gr", kcal=150, protein=15, carbs=1, fat=10, price=3.0)
    r = calc_ingredient_macros(ing, 100)
    assert r["kcal"] == 150.0
    assert r["price"] == 0.3


def test_calc_ingredient_macros_u():
    ing = SimpleNamespace(unit="u", kcal=75, protein=6, carbs=0.5, fat=5, price=0.5)
    r = calc_ingredient_macros(ing, 2)
    assert r["kcal"] == 150.0
    assert r["price"] == 1.0


def test_calc_recipe_macros_compound():
    i1 = SimpleNamespace(unit="gr", kcal=100, protein=10, carbs=5, fat=8, price=1.0)
    i2 = SimpleNamespace(unit="u", kcal=50, protein=6, carbs=2, fat=3, price=0.2)
    items = [
        SimpleNamespace(ingredient_id=1, quantity=200),
        SimpleNamespace(ingredient_id=2, quantity=2),
    ]
    r = calc_recipe_macros(items, {1: i1, 2: i2})
    assert r["kcal"] == 300.0
    assert r["price"] == 0.6


def test_estimate_1rm_epley():
    assert abs(estimate_1rm(100, 5) - 116.67) < 0.001


def test_estimate_1rm_single_rep():
    assert abs(estimate_1rm(100, 1) - 103.33) < 0.001
