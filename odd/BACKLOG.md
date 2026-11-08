# Backlog

> Colas de trabajo del proyecto. Un item del backlog = una feature futura
> que, cuando se apruebe, se convierte en `odd/tasks/<feature>.md` (ciclo SDD+ODD).

## Reglas

1. Un item = una feature (no tareas sueltas).
2. Nada se implementa sin pasar por `odd/tasks/<feature>.md` (SPECIFY → CLARIFY → PLAN → TASKS).
3. Los items se ordenan por prioridad: `P0` (ahora) / `P1` (próximo) / `P2` (despues) / `P3` (idea).
4. Este archivo es el único lugar donde se propone trabajo nuevo.
5. Al empezar una feature → el item se mueve a `odd/tasks/<feature>.md` y desaparece de Propuestos.
6. Al cerrarla (todas las tareas ✅ + Verification rellenada en `odd/tasks/<feature>.md`) → se lista en **Finalizados** con fecha.
7. El agente mantiene el backlog al día: al arrancar una feature su item pasa a ➡️ En curso; al cerrarla, a 🏁 Finalizados. El backlog es la cola única de trabajo: no se arranca nada que no esté aprobado aquí.
8. Each feature is developed on its own branch `feat/<feature-name>`, created when the feature starts. A fix to a feature is made on a `fix/<feature-name>` branch.

## Estados

| Estado | Significado |
|--------|-------------|
| 📥 Propuesto | Pendiente de revisión con el usuario |
| ✅ Aprobado | Revisado y aprobado; listo para SPECIFY |
| ➡️ En curso | Ya tiene `odd/tasks/<feature>.md` |
| 🏁 Finalizado | Cerrada: todas las tareas ✅ y Verification rellenada en `odd/tasks/<feature>.md` |
| ❌ Descartado | Revisado y descartado (dejar nota de por qué) |

---

## 📥 Propuestos

> Se rellena tras revisión con el usuario. Vacío = sin pendientes.

| # | Prioridad | Feature | Estado | Nota |
|---|-----------|---------|--------|------|
| 2 | P0 | `services-nutrition` | ✅ Aprobado | Ingredient, Recipe, Meal, Goal (provisional, cascadas, resumen diario) + tests. |
| 3 | P0 | `services-training` | ✅ Aprobado | Exercise, Workout (sets, PRs, 1RM estimado) + tests. |
| 4 | P0 | `mcp-server` | ✅ Aprobado | Registrar las 19 tools con schema real (SDK `mcp`), errores JSON según api-spec + tests integration. |
| 5 | P1 | `specs-completion` | ✅ Aprobado | Rellenar `requirements.md`, `api-spec.md` (cortada en línea 21), `data-model.md` (vacía). |
| 6 | P1 | `hermes-e2e` | ✅ Aprobado | Verificación end-to-end con cliente MCP real (Hermes). |
| 7 | P2 | `db-robustness` | ✅ Aprobado | Rollback en `get_db()` (pendiente de cierre de db-layer). |
| 8 | P3 | `seed-data` | ✅ Aprobado | Catálogo inicial de ingredientes/ejercicios. |
| 9 | P2 | `odd-merge-back` | ✅ Aprobado | Al cerrar, reflujar los criterios cumplidos a `docs/specs/` globales (imita el merge de deltas de OpenSpec; cierra el punto débil del ODD). |

> Orden recomendado de ejecución: `translate-to-english` → 2/3 → 4 (dependencias). 5 puede ir en paralelo.

---

## ➡️ En curso

| Feature | Archivo |
|---------|---------|
| `translate-to-english` | `odd/tasks/translate-to-english.md` |

---

## 🏁 Finalizados

| Feature | Archivo | Fecha |
|---------|---------|-------|
| db-layer | `odd/tasks/db-layer.md` | 2026-11 |
| utils-core | `odd/tasks/utils-core.md` | 2026-11 |

---

## ❌ Descartados

| Feature | Motivo |
|---------|--------|
| — | — |
