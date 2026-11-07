# Feature: utils-core

> Búsqueda fuzzy + cálculo de macros y precios. Utilidades puras, sin estado ni I/O. Base de todo lo demás.

## Spec
> Qué y por qué (sin tecnología)

- [ ] Criterio 1: Se puede normalizar un nombre (lowercase, sin acentos, sin espacios extra).
- [ ] Criterio 2: Se puede encontrar el candidato más parecido a una consulta entre una lista de opciones (o None si ninguna alcanza el umbral).
- [ ] Criterio 3: Se calculan macros y precio de una cantidad de ingrediente según su unidad (u/gr/ml).
- [ ] Criterio 4: Se calculan macros y precio totales de una receta sumando sus ingredientes.
- [ ] Criterio 5: Se estima el 1RM con la fórmula de Epley para cualquier nº de reps.
- [ ] Criterio 6: Todas las salidas numéricas se redondean a 2 decimales.

## Clarify
> Ambigüedades resueltas

- P: ¿Métrica y umbral del fuzzy? → R: `difflib.SequenceMatcher.ratio()` ∈ [0,1], umbral default **0.6** (parámetro opcional). Devuelve el mejor candidato si ratio ≥ umbral; si no, `None`.
- P: ¿Cómo se escalan las macros según unidad? → R: `u` → `valor × cantidad`; `gr` → `valor_por_100gr × (cantidad/100)`; `ml` → `valor_por_100ml × (cantidad/100)`. (Ej: 100gr huevo = 150kcal.)
- P: ¿Cómo se escala el precio? → R: referencia distinta a las macros. `u` → `price × cantidad`; `gr` → `price × (cantidad/1000)` (por kg); `ml` → `price × (cantidad/1000)` (por L). Moneda = **euro €**.
- P: ¿Redondeo? → R: **2 decimales** en todas las salidas numéricas.
- P: ¿1RM con 1 rep? → R: siempre Epley `weight × (1 + reps/30)`, sin caso especial para 1 rep.

## Plan
> Decisiones técnicas + clasificación

- **Clasificación**: Sustancial (funciones puras, 2 archivos, sin estado ni I/O, base de services-nutrition y services-training).
- D1: `normalize` con `unicodedata.normalize('NFKD', ...)` + strip de combining marks + `lower()` + collapse de espacios (`' '.join(s.split())`).
- D2: `fuzzy_match` con `difflib.SequenceMatcher.ratio()`, umbral como parámetro opcional (default 0.6). Itera candidatos, guarda el mejor ratio; si el máximo < umbral → `None`.
- D3: `calc_ingredient_macros` duck-typed (lee `.unit`, `.kcal`, `.protein`, `.carbs`, `.fat`, `.price`), escala macros y precio por separado según unidad.
- D4: `calc_recipe_macros` itera `recipe_items`, resuelve `ingredients[item.ingredient_id]` y suma los dicts de `calc_ingredient_macros`.
- D5: `estimate_1rm` = Epley directo, sin caso especial.
- D6: Redondeo con `round(x, 2)` al construir el dict de salida (no en cada operación intermedia, para evitar error acumulado).
- D7: Sin dependencias de DB: los utils reciben objetos ya cargados. Tests usan `SimpleNamespace` mocks (no tocan SQLite).

## Tasks
> Checklist de implementación

- [x] T1: Implementar `normalize()` en `src/utils/fuzzy.py` → files: src/utils/fuzzy.py → verify: `python -c "from src.utils.fuzzy import normalize; assert normalize('  Huevo  DE   Pavo ')=='huevo de pavo'; assert normalize('Ñandú')=='nandu'; print('OK')"`
- [x] T2: Implementar `fuzzy_match()` en `src/utils/fuzzy.py` → files: src/utils/fuzzy.py → verify: `python -c "from src.utils.fuzzy import fuzzy_match; assert fuzzy_match('huevo',['huevo','leche'])=='huevo'; assert fuzzy_match('huevo',['huevo','leche'])=='huevo'; assert fuzzy_match('zzz',['huevo','leche']) is None; print('OK')"`
- [x] T3: Implementar `calc_ingredient_macros()` en `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import calc_ingredient_macros as c; from types import SimpleNamespace as N; r=c(N(unit='gr',kcal=150,protein=12,carbs=1,fat=10,price=3.0),100); assert r['kcal']==150.0 and r['price']==0.3; r2=c(N(unit='u',kcal=75,protein=6,carbs=0,fat=5,price=0.5),2); assert r2['kcal']==150.0 and r2['price']==1.0; print('OK')"`
- [x] T4: Implementar `calc_recipe_macros()` en `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import calc_recipe_macros as c; from types import SimpleNamespace as N; i1=N(unit='gr',kcal=100,protein=5,carbs=10,fat=3,price=1.0); i2=N(unit='u',kcal=50,protein=2,carbs=1,fat=4,price=0.2); r=c([N(ingredient_id=1,quantity=200),N(ingredient_id=2,quantity=2)],{1:i1,2:i2}); assert r['kcal']==300.0 and r['price']==0.6; print('OK')"`
- [ ] T5: Implementar `estimate_1rm()` en `src/utils/macros.py` → files: src/utils/macros.py → verify: `python -c "from src.utils.macros import estimate_1rm; assert abs(estimate_1rm(100,5)-116.67)<0.01; assert abs(estimate_1rm(100,1)-103.33)<0.01; print('OK')"`
- [ ] T6: Rellenar `tests/unit/test_fuzzy_utils.py` (5 tests: exact, typo, no_match, accents, case/spaces) → files: tests/unit/test_fuzzy_utils.py → verify: `pytest tests/unit/test_fuzzy_utils.py -v`
- [ ] T7: Rellenar `tests/unit/test_macros_utils.py` (5 tests: gr, u, compound, epley, single_rep) → files: tests/unit/test_macros_utils.py → verify: `pytest tests/unit/test_macros_utils.py -v`

## Verification
> Contraste con spec (se rellena al cerrar)

- Criterio 1 (normalizar nombre): 
- Criterio 2 (fuzzy match): 
- Criterio 3 (macros por unidad): 
- Criterio 4 (macros receta): 
- Criterio 5 (1RM Epley): 
- Criterio 6 (redondeo 2 dec): 

## Close
> Cierre (se rellena al cerrar)

- **Estado**: 
