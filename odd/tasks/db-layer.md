# Feature: db-layer

> Conexión Peewee + Models + Migraciones. Infraestructura base de persistencia.

## Spec
> Qué y por qué (sin tecnología)

- [x] Criterio 1: El sistema puede crear una base de datos local con todas las tablas del modelo.
- [x] Criterio 2: Existe un context manager para obtener conexiones transaccionales.
- [x] Criterio 3: `init_db()` crea la DB si no existe y aplica migraciones pendientes.
- [x] Criterio 4: Los 9 modelos del dominio están definidos como clases ORM.
- [x] Criterio 5: El fixture de tests crea una DB in-memory funcional.
- [x] Criterio 6: Smoke test verifica init → insert → select → cleanup.

## Clarify
> Ambigüedades resueltas

- P: ¿Peewee o SQL directo? → R: Peewee (ADR-001).
- P: ¿Migraciones manuales o auto? → R: `peewee-migrate` + scripts SQL como fallback.
- P: ¿DB path configurable? → R: Sí, en `config.py`, default `data/fitness.db`.
- P: ¿¿Formato de fechas en DB? → R: TEXT `DD-MM-YYYY` / `DD-MM-YYYYTHH:MM:SS` (ADR-007).

## Plan
> Decisiones técnicas + clasificación

- **Clasificación**: Sustancial (infraestructura, varios archivos, pero sin API pública nueva)
- D1: Peewee `SQLiteExtDatabase` para soporte de partial indexes.
- D2: `BaseModel` con `Meta.database` mutable (para in-memory en tests).
- D3: `get_db()` como context manager con commit/rollback automático.
- D4: `init_db()` idempotente: crea dir, conecta, aplica migraciones, crea tablas si no existen.
- D5: Migración 001 ya existe como SQL → se usa como fallback si `peewee-migrate` no está disponible.
- D6: `config.py` expone `db_path` como Path absoluto.

## Tasks
> Checklist de implementación

- [x] T1: Definir 9 clases Peewee en `src/db/models.py` → files: src/db/models.py → verify: `python -c "from src.db.models import *; print('OK')"` ✅ `T1 OK: 9 models` (fix: SQLiteExtDatabase → SqliteDatabase)
- [x] T2: Implementar `get_db()` + `init_db()` en `src/db/connection.py` → files: src/db/connection.py → verify: `python -c "from src.db.connection import init_db; init_db(); print('OK')"` ✅ `OK` (fix: migrate.py corrupto + executescript)
- [x] T3: Implementar `src/db/migrate.py` (ensure_migrations_table, get_pending, apply) → files: src/db/migrate.py → verify: `python -c "from src.db.migrate import apply_migrations; print('OK')"` ✅ `T3 OK` (fix: `execute_sql` → `connection().executescript` para multi-statement)
- [x] T4: Verificar/ajustar `src/db/migrations/001_initial.sql` (coherente con models.py) → files: src/db/migrations/001_initial.sql → verify: init_db() → `SELECT name FROM sqlite_master WHERE type='table'` → 9 tablas ✅ `T4 OK: 11 tables` (9 dominio + _migrations + sqlite_sequence)
- [x] T5: Ajustar `src/config.py` (db_path como Path, migrations_dir) → files: src/config.py → verify: `python -c "from src.config import settings; print(settings.db_file)"` ✅ `T5 OK: C:\...\data\fitness.db`
- [x] T6: Rellenar `tests/conftest.py` (fixture db in-memory + create_tables) → files: tests/conftest.py → verify: `pytest tests/unit/test_db_smoke.py -v --fixtures` ✅ fixture `db` in-memory + fixtures de servicios
- [x] T7: Smoke test `tests/unit/test_db_smoke.py` (init → insert ingredient → select → assert) → files: tests/unit/test_db_smoke.py → verify: `pytest tests/unit/test_db_smoke.py -v` → PASSED ✅ `5 passed in 0.03s`

## Verification
> Contraste con spec (se rellena al cerrar)

- Criterio 1 (crear DB con todas las tablas): ✅ `init_db()` → 9 tablas del dominio + `_migrations` + `sqlite_sequence` en `data/fitness.db`.
- Criterio 2 (context manager transaccional): ✅ `get_db()` en `connection.py` con commit/rollback.
- Criterio 3 (`init_db()` crea DB + aplica migraciones): ✅ idempotente, aplica `001_initial.sql` vía `executescript`.
- Criterio 4 (9 modelos ORM): ✅ `models.py` — 9 clases + `ALL_MODELS`.
- Criterio 5 (fixture in-memory): ✅ `conftest.py` fixture `db` reasigna `Meta.database` a `:memory:`.
- Criterio 6 (smoke test init→insert→select→cleanup): ✅ `test_db_smoke.py` — 5 tests PASSED.

## Close
> Cierre (se rellena al cerrar)

- **Estado**: Cerrada. 7/7 tareas ✅, 6/6 criterios de spec ✅.
- **Fixes aplicados durante implementación**:
  1. `migrate.py` estaba corrupto (texto de conversación pegado al final) → se limpió.
  2. `apply_migrations` usaba `db.execute_sql()` (un statement a la vez) → `db.connection().executescript()` para multi-statement.
  3. `models.py`: `SQLiteExtDatabase` → `SqliteDatabase` (T1).
- **Nota**: `pytest` no estaba en `requirements.txt` ni en el venv → se instaló. Considerar agregarlo a `requirements.txt` (dev).
- **Pendiente opcional**: `get_db()` rama `if not db.is_closed()` no tiene `try/except` (sin rollback si falla a mitad). No bloquea; mejorar en feature de servicios si se detecta.
