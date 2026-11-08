# Decisiones de Arquitectura (ADR)

> Registro de decisiones arquitectónicas. Cada ADR: contexto, decisión, consecuencias.

---

## ADR-001: Python + SQLite + Peewee

**Fecha**: 2025-01-15
**Estado**: Aceptado

### Contexto
Sistema local de un solo usuario. No hay necesidad de escalabilidad. Se requiere simplicidad y mínimo overhead.

### Decisión
- **Lenguaje**: Python 3.11+
- **Base de datos**: SQLite 3 (archivo local `data/fitness.db`)
- **ORM**: Peewee (ligero, sin dependencias pesadas como SQLAlchemy)
- **Migraciones**: `peewee-migrate` + scripts SQL manuales

### Consecuencias
- ✅ Cero infraestructura externa. Un archivo `.db` es toda la persistencia.
- ✅ Peewee es minimalista, fácil de debuguear, sin magic.
- ✅ Migraciones simples para un solo usuario.
- ❌ No escalable a multi-usuario (no es un requisito).
- ❌ Sin réplicas

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
