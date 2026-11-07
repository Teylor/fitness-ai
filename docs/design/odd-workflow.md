# Ciclo de Trabajo SDD + ODD

> Proceso obligatorio para cualquier cambio en el proyecto. El agente impone este orden.

## Principio

> **No se implementa sin spec.** Antes de tocar código, se revisan y actualizan las specs.
> Una vez aprobadas por el usuario, se empieza la implementación.

---

## Fase 0 — BACKLOG (gate de entrada)

> Antes de SPECIFY, el trabajo debe existir como item en `odd/BACKLOG.md` (📥 Propuesto → ✅ Aprobado).
> Al arrancar la feature, el item pasa a ➡️ En curso. Al cerrarla, a 🏁 Finalizados.
> El backlog es la cola única de trabajo: no se arranca nada que no esté aprobado ahí.

---

## Ciclo completo

```
Petición del usuario
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. SPECIFY                                                         │
│    Describir la feature: QUÉ y POR QUÉ (sin tecnología).           │
│    Criterios de aceptación claros.                                 │
│    → odd/tasks/<feature>.md (sección "Spec")                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. CLARIFY                                                         │
│    El agente lista ambigüedades, supuestos y preguntas.            │
│    Se resuelven TODAS antes de seguir.                             │
│    → odd/tasks/<feature>.md (sección "Clarify")                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. PLAN                                                            │
│    Decisiones técnicas alineadas con la constitución (ADR).        │
│    Arquitectura, dependencias, riesgos.                            │
│    → odd/tasks/<feature>.md (sección "Plan")                       │
│    → docs/architecture/ssd-decisions.md (si hay ADR nuevo)         │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. TASKS                                                           │
│    Lista de tareas pequeñas, cada una con:                          │
│      - Descripción                                                 │
│      - Verificación (test, comando, o inspección manual)           │
│      - Estado: [ ] → [~] → [x]                                    │
│    → odd/tasks/<feature>.md (sección "Tasks")                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. IMPLEMENT                                                       │
│    Una tarea por vez. TDD si está configurado.                     │
│    Commit por tarea. Marcar progreso en el checklist.              │
│    → src/ (código)                                                 │
│    → odd/tasks/<feature>.md (marcar [x] + evidencia)               │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. REVIEW / VERIFY                                                 │
│    Contrastar resultado con el spec (no con "parece que funciona").│
│    Cada criterio de aceptación → verificado.                       │
│    → odd/tasks/<feature>.md (sección "Verification")               │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. CLOSE                                                           │
│    Cerrar criterios de aceptación.                                 │
│    Actualizar docs (specs, ADRs, modelos).                         │
│    Dejar "siguiente paso" si hay follow-up.                        │
│    → odd/tasks/<feature>.md (sección "Close")                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Escalado a SDD (rama completa)

No toda feature necesita el ciclo completo. `classify` decide:

| Tamaño | Criterios | Rama |
|--------|-----------|------|
| **Trivial** | 1 archivo, cambio de typo, rename, config | Implement directo (sin spec) |
| **Pequeño** | 1-2 archivos, 1 módulo, sin API pública | Spec mínima + tasks + implement |
| **Sustancial** | Varios módulos, nueva entidad, nueva tool MCP | Spec completa + clarify + plan + tasks + implement + verify |
| **Necesita SDD** | Cambia contrato público/API, migración de datos, seguridad, difícil de revertir, varios agentes en paralelo | SDD completo (spec.md + plan.md separados) |

### Criterios de escalado a SDD (cualquiera de estos):
- Cambia un contrato público o API (tool MCP)
- Toca varios módulos simultáneamente
- Los requisitos son ambiguos o hay múltiples interpretaciones
- Afecta a seguridad o migración de datos
- Es difícil de revertir
- Varios agentes trabajarán en paralelo

---

## Estructura de archivos por feature

```
odd/
├── BACKLOG.md                     # Cola única de trabajo (Propuesto → Aprobado → En curso → Finalizado)
└── tasks/
    └── <feature-name>.md          # Checklist único (fuente de verdad)

specs/
└── <feature-name>/
    ├── spec.md                   # (solo SDD) Qué y por qué
    └── plan.md                   # (solo SDD) Decisiones técnicas
```

### Plantilla `odd/tasks/<feature>.md`

```markdown
# Feature: <nombre>

## Spec
> Qué y por qué (sin tecnología)

- [ ] Criterio de aceptación 1
- [ ] Criterio de aceptación 2

## Clarify
> Ambigüedades resueltas

- P: ¿...? → R: ...

## Plan
> Decisiones técnicas

- D1: ...
- D2: ...

## Tasks
> Checklist de implementación

- [ ] T1: <descripción> → verify: <test/comando>
- [ ] T2: <descripción> → verify: <test/comando>

## Verification
> Contraste con spec

- [x] Criterio 1: ✅ <evidencia>
- [x] Criterio 2: ✅ <evidencia>

## Close
> Cierre

- Fecha: ...
- Siguiendo paso: ...
```

---

## Reglas de integración

1. **Una sola fuente de progreso.** El checklist vive solo en `odd/tasks/<feature>.md`. El spec nunca guarda estado.
2. **Criterios de escalado.** Si `classify` dice "necesita SDD" → se crean `specs/<feature>/spec.md` y `plan.md` separados.
3. **Cambios sobre una feature con spec.** Se editan primero en `spec.md`, luego se regenera `plan.md` y se reabren las tareas afectadas en el documento ODD, con motivo.
4. **Escalado a mitad de camino.** Si durante `implement-task` aparece complejidad inesperada, se detiene, se reclasifica y se entra en la rama SDD sin perder lo ya hecho.
5. **Cambio solo de implementación.** No se toca el spec.
6. **Aprobación del usuario.** Antes de `implement`, el usuario debe aprobar spec + plan + tasks.
7. **Backlog como cola única.** El agente consulta `odd/BACKLOG.md` antes de empezar y actualiza el estado del item al arrancar (➡️ En curso) y al cerrar (🏁 Finalizados). No se arranca una feature sin item aprobado.

---

## Skills del núcleo ODD (siempre activas)

| Skill | Qué hace |
|-------|----------|
| `odd-protocol` | Orquestador. Impone el orden: consultar BACKLOG, autorizar, explorar, resolver incertidumbre, clasificar, registrar, implementar, cerrar. |
| `explore` | Lee el código real, tests y ADRs relevantes antes de proponer nada. |
| `classify` | Decide el tamaño: trivial, pequeño, sustancial o necesita spec. |
| `track-feature` | Crea o actualiza `odd/tasks/<feature>.md` antes de la primera escritura. |
| `implement-task` | Una tarea por vez, con TDD si está configurado, y marca progreso y evidencia. |
| `close-feature` | Cierra criterios de aceptación, actualiza el documento, deja el siguiente paso y marca 🏁 Finalizado en `odd/BACKLOG.md`. |

## Skills de la rama SDD (solo si classify escala)

| Skill | Qué hace |
|-------|----------|
| `sdd-specify` | Escribe `specs/<feature>/spec.md`: qué y por qué, sin tecnologías. |
| `sdd-clarify` | Lista ambigüedades y las resuelve antes de seguir. |
| `sdd-plan` | Escribe `plan.md`: arquitectura, decisiones y riesgos, alineado con la constitución. |
| `sdd-tasks` | Convierte el plan en checklist dentro del documento ODD, no en un tasks.md aparte. |
| `sdd-verify` | Contrasta código contra spec. Opcional, de diagnóstico, no bloquea el cierre. |
| `sdd-archive` | Al cerrar, marca el spec como implementado y lo mueve a su histórico. |

---

## Cómo se conectan

```
Petición → odd-protocol (consultar BACKLOG) → explore → classify
                                │
                                ├─ trivial/pequeño ──────────→ track-feature → implement-task → close
                                │
                                └─ necesita spec → sdd-specify → sdd-clarify → sdd-plan → sdd-tasks
                                                                        │
                                                                        ▼
                                                            track-feature (enlaza spec y plan)
                                                                        │
                                                                        ▼
                                                            implement-task → close
                                                                        │
                                                                        ▼
                                                            sdd-verify (opcional) → sdd-archive
```

---

## Planificación de tests

| Versión | Scope | Herramienta |
|---------|-------|-------------|
| **v0** | Tests unitarios por service (CRUDs, cálculos macros, PR) + tests de integración MCP (llamar tool → verificar JSON) | `pytest` + `pytest-asyncio` |
| **v1** | Tests e2e: simular flujo completo Hermes → MCP → DB → respuesta | `pytest` + fixture de DB temporal |

### Estructura tests (v0)

```
tests/
├── __init__.py
├── conftest.py              # Fixtures: DB temporal, services, MCP client
├── unit/
│   ├── test_ingredient_service.py
│   ├── test_recipe_service.py
│   ├── test_meal_service.py
│   ├── test_goal_service.py
│   ├── test_exercise_service.py
│   ├── test_workout_service.py
│   ├── test_macros_utils.py
│   └── test_fuzzy_utils.py
└── integration/
    ├── test_mcp_meal_tools.py
    ├── test_mcp_ingredient_tools.py
    ├── test_mcp_recipe_tools.py
    ├── test_mcp_goal_tools.py
    ├── test_mcp_workout_tools.py
    └── test_mcp_exercise_tools.py
```

### Regla TDD en implement-task

1. **Antes** de implementar una tarea → escribir el test (rojo).
2. **Implementar** la tarea (verde).
3. **Refactorizar** si hace falta.
4. **Commit** con mensaje: `feat(<module>): <tarea> [T#]`
5. Marcar `[x]` en `odd/tasks/<feature>.md` con evidencia: `pytest tests/unit/test_x.py::test_y -v` → PASSED
