"# Skill: implement-task

> Una tarea por vez, con TDD si está configurado, y marca progreso y evidencia.

## Cuándo se activa
Después de `track-feature` (checklist aprobado por usuario).

## Pasos

1. **Seleccionar** la primera tarea `[ ]` del checklist en `odd/tasks/<feature>.md`.
2. **TDD** (si está configurado):
   a. Escribir el test primero (rojo).
   b. Ejecutar → debe fallar.
3. **Implementar** la tarea.
4. **Verificar**:
   - Ejecutar test → debe pasar (verde).
   - Ejecutar comando de verificación especificado en la tarea.
5. **Commit**: `feat(<module>): <descripción> [T#]`
6. **Marcar** en `odd/tasks/<feature>.md`:
   - `[x] T#: <descripción> → verify: <evidencia: pytest output, comando, etc.>`
7. **Repetir** con la siguiente tarea.

## Reglas
- **Una tarea por vez.** No agrupar.
- Si una tarea requiere más de lo esperado → detenerse, reclasificar (→ `classify`).
- Si un test falla → no pasar a la siguiente hasta arreglar.
- Si aparece complejidad inesperada → escalar a SDD (→ `sdd-specify`).
- Evidencia obligatoria: sin evidencia, la tarea no está hecha.
- Commit por tarea (no agrupar commits).

## Formato de evidencia

```
- [x] T3: Implementar calc_recipe_macros → verify: pytest tests/unit/test_macros_utils.py::test_calc_recipe -v → PASSED (3 tests)
```
"