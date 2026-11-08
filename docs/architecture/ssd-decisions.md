# Architecture Decisions (ADR)

> Registry of architectural decisions. Each ADR: context, decision, consequences.

---

## ADR-001: Python + SQLite + Peewee

**Date**: 2025-01-15
**Status**: Accepted

### Context
Single-user local system. There is no scalability requirement. Simplicity and minimal overhead are required.

### Decision
- **Language**: Python 3.11+
- **Database**: SQLite 3 (local file `data/fitness.db`)
- **ORM**: Peewee (lightweight, no heavy dependencies like SQLAlchemy)
- **Migrations**: `peewee-migrate` + manual SQL scripts

### Consequences
- ✅ Zero external infrastructure. A single `.db` file is all the persistence.
- ✅ Peewee is minimalist, easy to debug, no magic.
- ✅ Simple migrations for a single user.
- ❌ Not scalable to multi-user (not a requirement).
- ❌ No replicas

---

## ADR-002: Project language is English

**Date**: 2026-11-08
**Status**: Accepted

### Context
All project artifacts (docs, specs, ODD, ADRs, READMEs, code comments/docstrings, test descriptions, SQL and script comments) were written in Spanish. To keep the codebase consistent and broadly readable, the project standardizes on a single language.

### Decision
- All project artifacts are written in **English**: docs, specs, architecture, ODD, ADRs, READMEs, code comments/docstrings, test docstrings/assertion messages, SQL comments, and script comments.
- Code identifiers, imports, syntax, and technical terms are unaffected (they already follow Python/SQL conventions).
- Existing Spanish content is migrated to English by the `translate-to-english` feature; no new Spanish content is added from now on.

### Consequences
- ✅ One consistent language across the whole project.
- ✅ New readers/contributors need no Spanish.
- ⚠️ Test fixtures that intentionally exercise accent/normalization behavior (e.g. `normalize("Café")`, `normalize("Ñandú")`) are preserved as-is, because the accented input is the point of those tests.
