"# Skill: close-feature

> Cierra criterios de aceptación, actualiza el documento y deja el siguiente paso.

## Cuándo se activa
Cuando todas las tareas del checklist están `[x]`.

## Pasos

1. **Verificar** que todas las tareas están `[x]` en `odd/tasks/<feature>.md`.
2. **Rellenar sección Verification**:
   - Para cada criterio de aceptación del spec → evidencia de que está cumplido.
   - Ejecutar tests completos: `pytest tests/ -v`
3. **Actualizar docs** si hace falta:
   - `docs/design/odd-models.md` (si se añadió entidad)
   - `docs/specs/openspec/api-spec.md` (si se añadió tool MCP)
   - `docs/specs/openspec/data-model.md` (si se añadió tabla)
   - `docs/architecture/ssd-decisions.md` (si hay ADR nuevo)
4. **Rellenar sección Close**:
   - Fecha de cierre.
   - Resumen de lo implementado.
   - "Siguiente paso" si hay follow-up pendiente.
5. **Commit final**: `feat(<module>): close <feature> [all tasks done]`

## Reglas
- No cerrar sin verificar TODOS los criterios de aceptación.
- Si falta algo → no cerrar, añadir tarea al checklist.
- Si hay follow-up → documentarlo en "Siguiente paso", no bloquear el cierre.
- Si es rama SDD → invocar `sdd-archive` después.
"