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
