# Feature: db-robustness

> Improve SQLite connection lifecycle, transaction rollback, and PRAGMA settings (WAL mode, foreign keys, busy timeout).

## Spec
> What and why (no technology)

### Context
- The SQLite persistence layer relies on Peewee ORM with a shared database connection.
- Currently, `get_db()` is a generator missing `@contextmanager`, causing runtime failures if invoked with a `with` statement.
- Furthermore, the unclosed branch in `get_db()` lacks transaction protection and rollback on error, which could leave half-applied transactions on unhandled exceptions.
- In SQLite, foreign key enforcement is turned off by default (`PRAGMA foreign_keys = 0`), which risks orphaned records or broken relational consistency.
- SQLite default journal mode is `delete`, which blocks concurrent readers and writers, occasionally leading to `OperationalError: database is locked` on multi-client MCP queries or persistent 24/7 server access.

### Objective
- Ensure `get_db()` works as a robust, transactional context manager with automatic commit on success and automatic rollback on failure, including nested transaction (savepoint) support.
- Ensure SQLite PRAGMAs are systematically enabled:
  - `foreign_keys = ON` to enforce relational constraints.
  - `journal_mode = WAL` (Write-Ahead Logging) to allow concurrent reads during writes.
  - `busy_timeout = 5000` (5 seconds) to prevent immediate locks under concurrent access.
  - `synchronous = NORMAL` for optimal durability and write performance in WAL mode.
- Ensure transparent reconnection if the connection is closed or drops.

### Acceptance Criteria
- [x] C1: **Context Manager Protocol**: `get_db()` is decorated with `@contextmanager` and can be used with `with get_db() as connection: ...`.
- [x] C2: **Transactional Atomicity & Rollback**: Any exception raised inside `with get_db():` causes all operations in that block to roll back cleanly without persisting changes to the database.
- [x] C3: **Commit on Success**: Operations completed successfully inside `with get_db():` are committed to disk.
- [x] C4: **Nested Transactions**: `get_db()` supports nesting via savepoints without crashing or committing prematurely.
- [x] C5: **PRAGMA Enforcement**: SQLite connection initializes with `foreign_keys = 1`, `journal_mode = wal`, `busy_timeout = 5000`, and `synchronous = normal`.
- [x] C6: **Foreign Key Protection**: Attempting to insert a child row with a non-existent foreign key (e.g., `RecipeItem` with invalid `recipe_id`) raises `IntegrityError`.
- [x] C7: **Test Coverage**: Dedicated tests in `tests/unit/test_db_robustness.py` verify all transactional behaviors, rollbacks, and PRAGMAs.

## Clarify
> Ambiguities resolved

- **Q1. Should `get_db()` use Peewee's native `db.atomic()`?**
  - A: Yes. `db.atomic()` natively supports context manager protocol, savepoints, nested blocks, and automatic rollback on exceptions.
- **Q2. How should PRAGMAs be configured on Peewee `SqliteDatabase`?**
  - A: Peewee supports a `pragmas` dictionary in `SqliteDatabase(..., pragmas={...})` and `db.init(..., pragmas={...})`, and `init_db()` can explicitly execute them.
- **Q3. Does in-memory test database support WAL mode?**
  - A: SQLite in-memory databases (`:memory:`) ignore WAL mode (`journal_mode = memory`), but they fully support `foreign_keys = 1` and `busy_timeout`. Test assertions should account for `:memory:` vs disk differences.

## Plan
> Technical decisions + classification

- **Classification**: Normal (core database connection and transaction handling).
- **D1 (Context Manager & Transactions)**:
  - In `src/db/connection.py`: Decorate `get_db()` with `@contextmanager`.
  - Reconnect safely if closed: `if db.is_closed(): db.connect(reuse_if_open=True)`.
  - Delegate transaction handling to `with db.atomic(): yield db`.
- **D2 (PRAGMA Configuration)**:
  - In `src/db/models.py`: Pass standard pragmas to default `db = SqliteDatabase("data/fitness.db", pragmas=...)`.
  - In `src/db/connection.py`: In `init_db()`, configure `db.init(str(db_path), pragmas=...)` and execute PRAGMAs on connection.
- **D3 (Tests)**:
  - Create `tests/unit/test_db_robustness.py` testing:
    1. `test_get_db_commits_on_success`
    2. `test_get_db_rolls_back_on_error`
    3. `test_get_db_nested_savepoints`
    4. `test_foreign_keys_enforced`
    5. `test_pragmas_applied_on_disk_db`

## Tasks
> Implementation checklist

- [x] T1: Update `src/db/connection.py` with `@contextmanager`, `db.atomic()`, and PRAGMA settings.
- [x] T2: Update `src/db/models.py` with default pragmas.
- [x] T3: Create `tests/unit/test_db_robustness.py` covering transactions, rollbacks, nested blocks, and PRAGMAs.
- [x] T4: Run full test suite and verify backwards compatibility.

## Verification
> Spec contrast (filled at close)

- **C1 (Context Manager Protocol)**: `get_db()` is decorated with `@contextmanager` and safely yields the database instance within a Python `with` block. Verified by `test_get_db_commits_on_success`.
- **C2 (Transactional Atomicity & Rollback)**: Exceptions inside `with get_db():` trigger a rollback via Peewee atomic context manager, ensuring no partial writes persist. Verified by `test_get_db_rolls_back_on_error`.
- **C3 (Commit on Success)**: Normal exit from `with get_db():` commits all created records. Verified by `test_get_db_commits_on_success`.
- **C4 (Nested Transactions)**: `get_db()` uses `db.atomic()`, allowing nested transaction blocks via savepoints. Inner errors can be caught without aborting outer blocks. Verified by `test_get_db_nested_savepoints`.
- **C5 (PRAGMA Enforcement)**: `init_db()` and `SqliteDatabase` systematically configure `foreign_keys=1`, `journal_mode=wal`, `busy_timeout=5000`, and `synchronous=1` (NORMAL). Verified by `test_init_db_configures_pragmas` and live verification on `data/fitness.db`.
- **C6 (Foreign Key Protection)**: Inserting child records with non-existent foreign keys raises `IntegrityError` due to active `PRAGMA foreign_keys = 1`. Verified by `test_foreign_keys_enforced`.
- **C7 (Test Coverage)**: All 6 new robustness tests pass in `tests/unit/test_db_robustness.py`, and full test suite passes (168/168 tests).

## Close
> Close (filled at close)

- **Date**: 2026-11-10
- **Status**: Closed. 4/4 tasks ✅, 7/7 spec criteria ✅.
- **Artifacts**:
  - `src/db/connection.py`
  - `src/db/models.py`
  - `tests/conftest.py`
  - `tests/unit/test_db_robustness.py`
