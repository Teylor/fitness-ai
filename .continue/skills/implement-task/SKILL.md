"# Skill: implement-task

> Una tarea por vez, con TDD si está configurado, y marca progreso y evidencia.

## Cuándo se activa
Después de `track-feature` (checklist aprobado por usuario).

## Execution modes (rule 11, odd-workflow)

- **Slow (task-by-task):** the steps below apply as written — one task at a time, pre-commit report and proposed commit per task.
- **Fast (feature-by-feature, default):** run every task of the feature in one pass without per-task stops. Each task is still verified (tests pass) and marked `[x]` with evidence. When the feature is done, present ONE pre-commit report covering all its changes and propose a single commit.

## Pasos

1. **Seleccionar** la primera tarea `[ ]` del checklist en `odd/tasks/<feature>.md`.
2. **TDD** (si está configurado):
   a. Escribir el test primero (rojo).
   b. Ejecutar → debe fallar.
3. **Implementar** la tarea.
4. **Verificar**:
   - Ejecutar test → debe pasar (verde).
   - Ejecutar comando de verificación especificado en la tarea.
5. **Report pre-commit** (obligatorio, antes de cualquier commit):
   a. **Cambios hechos**: archivos afectados y qué se modificó en cada uno, con el porqué.
   b. **Tests (si aplican)**: qué tests cubren los cambios (nuevos y existentes) y su resultado. Si no hay tests aplicables → declararlo explícitamente.
   c. **Mensaje de commit sugerido**: `feat(<module>): <descripción> [T#]`
6. **Esperar la decisión del usuario** (no avanzar solo):
   - El usuario hace el commit (o pide al agente que lo haga con el mensaje acordado) → **Marcar** en `odd/tasks/<feature>.md`:
     - `[x] T#: <descripción> → verify: <evidencia: pytest output, comando, etc.>`
   - El usuario pide cambios → dejar la tarea en `[~]`, aplicar, re-verificar tests y repetir el report.
   - El usuario dice "continuar a la siguiente tarea" → **Marcar** `[x]` con evidencia (el commit queda a criterio del usuario).
7. **Repetir** con la siguiente tarea (solo tras la decisión del usuario; slow mode).

## Reglas
- **Una tarea por vez.** No agrupar (slow mode; see Execution modes).
- Si una tarea requiere más de lo esperado → detenerse, reclasificar (→ `classify`).
- Si un test falla → no pasar a la siguiente hasta arreglar.
- Si aparece complejidad inesperada → escalar a SDD (→ `sdd-specify`).
- Evidencia obligatoria: sin evidencia, la tarea no está hecha.
- Commit per task (no grouped commits) in slow mode; one proposed commit per feature in fast mode. The user runs the commit after the pre-commit report.
- El agente no ejecuta `git commit` por su cuenta.
- No avanzar a la siguiente tarea sin la decisión del usuario tras el report (slow mode; in fast mode advance after verifying the task).
- All new code text (docstrings, comments, test descriptions/assertion messages) is written in English (ADR-002).

## Formato de evidencia

```
- [x] T3: Implementar calc_recipe_macros → verify: pytest tests/unit/test_macros_utils.py::test_calc_recipe -v → PASSED (3 tests)
```
"