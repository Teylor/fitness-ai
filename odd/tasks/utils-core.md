# Feature: utils-core

> Fuzzy search + macro and price calculation. Pure utilities, no state or I/O. The base of everything else.

## Spec
> What and why (no technology)

- [ ] C1: A name can be normalized (lowercase, no accents, no extra spaces).
- [ ] C2: The candidate most similar to a query can be found among a list of options (or None if none reaches the threshold).
- [ ] C3: Macros and price of an ingredient quantity are calculated according to its unit (u/gr/ml).
- [ ] C4: Total macros and price of a recipe are calculated by summing its ingredients.
- [ ] C5: The 1RM is estimated with the Epley formula for any number of reps.
- [ ] C6: All numeric outputs are rounded to 2 decimals.

## Clarify
> Ambiguities resolved

- Q: Which metric and threshold for the fuzzy? → A: `difflib.SequenceMatcher.ratio()` ∈ [0,1], default threshold **0.6** (optional parameter). Returns the best candidate if ratio ≥ threshold; otherwise `None`.
- Q: How are macros scaled by unit? → A: `u` → `value × quantity`; `gr` → `value_per_100gr × (quantity/100)`; `ml` → `value_per_100ml × (quantity/100)`. (Eg: 100gr egg = 150kcal.)
- Q: How is price scaled? → A: reference distinct from macros. `u` → `price × quantity`; `gr` → `price × (quantity/1000)` (per kg); `ml` → `price × (quantity/1000)` (per L). Currency = **euro €**.
- Q: Rounding? → A: **2 decimals** in all numeric outputs.
- Q: 1RM with 1 rep? → A: always Epley `weight × (1 + reps/30)`, no special case for 1 rep.

## Plan
> Technical decisions + classification

- **Classification**: Substantial (pure functions, 2 files, no state or I/O, base of services-nutrition and services-training).
- D1: `normalize` with `unicodedata.normalize('NFKD', ...)` + strip of combining marks + `lower()` + space collapse (`' '.join(s.split())`).
- D2: `fuzzy_match` with `difflib.SequenceMatcher.ratio()`, threshold as optional parameter (default 0.6). Iterates candidates, keeps the best ratio; if the max < threshold → `None`.
- D3: `calc_ingredient_macros` duck-typed (reads `.unit`, `.kcal`, `.protein`, `.carbs`, `.fat`, `.price`), scales macros and price separately by unit.
- D4: `calc_recipe_macros` iterates `recipe_items`, resolves `ingredients[item.ingredient_id]` and sums the dicts from `calc_ingredient_macros`.
- D5: `estimate_1rm` = Epley direct, no special case.
- D6: Rounding with `round(x, 2)` when building the output dict (not in each intermediate operation, to avoid accumulated error).
- D7: No DB dependencies: the utils receive already-loaded objects. Tests use `SimpleNamespace` mocks (they don't touch SQLite).

## Tasks
> Implementation checklist

- [x] T1: Implement `normalize()` in `src/utils/fuzzy.py` → files: src/utils/fuzzy.py → verify: `python -c "from src.utils.fuzzy import normalize; assert normalize('  Egg  OF   Turkey ')=='egg of turkey'; assert normalize('Ñandú')=='nandu'; print('OK')"`
- [x] T2: Implement `fuzzy_match()` in `src/utils/fuzzy.py` → files: src/utils/fuzzy.py → verify: `python -c "from src.utils.fuzzy import fuzzy_match; assert fuzzy_match('egg',['egg','milk'])=='egg'; assert fuzzy_match('egg',['egg','milk'])=='egg'; assert fuzzy_match('zzz',['egg','milk']) is None; print('OK')"`
- [x] T3: Implement `calc_ingredient_macros()` in `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import calc_ingredient_macros as c; from types import SimpleNamespace as N; r=c(N(unit='gr',kcal=150,protein=12,carbs=1,fat=10,price=3.0),100); assert r['kcal']==150.0 and r['price']==0.3; r2=c(N(unit='u',kcal=75,protein=6,carbs=0,fat=5,price=0.5),2); assert r2['kcal']==150.0 and r2['price']==1.0; print('OK')"`
- [x] T4: Implement `calc_recipe_macros()` in `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import calc_recipe_macros as c; from types import SimpleNamespace as N; i1=N(unit='gr',kcal=100,protein=5,carbs=10,fat=3,price=1.0); i2=N(unit='u',kcal=50,protein=2,carbs=1,fat=4,price=0.2); r=c([N(ingredient_id=1,quantity=200),N(ingredient_id=2,quantity=2)],{1:i1,2:i2}); assert r['kcal']==300.0 and r['price']==0.6; print('OK')"`
- [x] T5: Implement `estimate_1rm()` in `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import estimate_1rm; assert abs(estimate_1rm(100,5)-116.67)<0.01; assert abs(estimate_1rm(100,1)-103.33)<0.01; print('OK')"`
- [x] T6: Fill `tests/unit/test_fuzzy_utils.py` (5 tests: exact, typo, no_match, accents, case/spaces) → files: tests/unit/test_fuzzy_utils.py → verify: `pytest tests/unit/test_fuzzy_utils.py -v`
- [x] T7: Fill `tests/unit/test_macros_utils.py` (5 tests: gr, u, compound, epley, single_rep) → files: tests/unit/test_macros_utils.py → verify: `pytest tests/unit/test_macros_utils.py -v`

## Verification
> Spec contrast (filled at close)

- C1 (normalize a name): `normalize()` in `src/utils/fuzzy.py` (NFKD + strip combining + lower + collapse). Covered by `test_normalize_accents` and `test_normalize_case_and_spaces` (T1 verify OK).
- C2 (fuzzy match): `fuzzy_match()` in `src/utils/fuzzy.py` (SequenceMatcher.ratio, threshold 0.6, else None). Covered by `test_fuzzy_match_exact/typo/no_match` (T2 verify OK).
- C3 (macros by unit): `calc_ingredient_macros()` in `src/utils/macros.py` (u: ×qty; gr/ml: ×qty/100; price u:×qty, gr:×qty/1000, ml:×qty/1000). Covered by `test_calc_ingredient_macros_gr/u` (T3 verify OK).
- C4 (recipe macros): `calc_recipe_macros()` in `src/utils/macros.py` (sums items indexed by `ingredient_id`). Covered by `test_calc_recipe_macros_compound` (T4 verify OK).
- C5 (1RM Epley): `estimate_1rm()` in `src/utils/macros.py` (weight × (1 + reps/30)). Covered by `test_estimate_1rm_epley/single_rep` (T5 verify OK).
- C6 (rounding 2 dec): `round(x, 2)` when building the output dict in T3/T4/T5 (outputs 150.0, 0.3, 0.6, 1.0, 116.67, 103.33). Verified in the asserts of `test_macros_utils.py`.

## Close
> Close (filled at close)

- **Status**: ✅ Done (7/7 tasks, 6/6 criteria; 10/10 unit tests OK)
- **Commits**: T1 `651f3f3` · T2 `85eff3c` · T3 `fe0a8df` · T4 `7a574f6` · T5 `e67b430` · T6 `608d4a9` · T7 `8ce85f2`
