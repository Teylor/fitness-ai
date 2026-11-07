"# Skill: sdd-verify

> Contrasta código contra spec. Opcional, de diagnóstico, no bloquea el cierre.

## Cuándo se activa
Opcional, después de `close-feature`. Útil cuando se quiere una verificación extra antes de archivar.

## Pasos

1. **Leer** `specs/<feature>/spec.md` (criterios de aceptación).
2. **Para cada criterio**:
   - Buscar en el código la implementación correspondiente.
   - Ejecutar el test asociado.
   - Verificar que el comportamiento real coincide con el spec.
3. **Reportar**:
   ```
   | Criterio | Estado | Evidencia |
   |----------|--------|-----------|
   | CA1 | ✅ | test_x.py::test_y PASSED |
   | CA2 | ✅ | Comando: `python -m src.main` → OK |
   | CA3 | ⚠️ | Parcial: falta edge case Z |
   ```
4. **Si hay discrepancias**:
   - No bloquear el cierre.
   - Documentar en `odd/tasks/<feature>.md` sección `## Verification`.
   - Crear nueva feature para el fix si es necesario.

## Reglas
- **No bloquea.** Es diagnóstico, no gate.
- Si el código no coincide con el spec → documentar, no arreglar aquí.
- Si el spec está mal (describe algo que no se quería) → editar spec, no código.
- Resultado se guarda en el documento ODD, no en el spec.
"