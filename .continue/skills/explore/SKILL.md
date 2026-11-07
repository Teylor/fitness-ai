"# Skill: explore

> Lee el código real, tests y ADRs relevantes antes de proponer nada.

## Cuándo se activa
Después de autorizar, antes de clasificar.

## Pasos

1. **Leer código relevante**:
   - `src/` → archivos que la feature toca o podría tocar.
   - `tests/` → tests existentes que cubren esa zona.
   - `docs/architecture/ssd-decisions.md` → ADRs que afectan la decisión.
   - `docs/design/odd-models.md` → entidades existentes.
   - `docs/specs/openspec/api-spec.md` → tools MCP existentes.

2. **Identificar**:
   - ¿Qué existe ya? (no re-inventar)
   - ¿Qué patrones se usan? (consistencia)
   - ¿Qué ADRs aplican? (no contradecir decisiones previas)
   - ¿Qué tests cubren la zona? (no romper lo que funciona)

3. **Resumir** al usuario:
   - "He revisado X, Y, Z. Esto es lo que ya existe. Esto es lo que falta."

## Reglas
- No proponer cambios sin haber leído el código afectado.
- Si un ADR contradice lo que se quiere hacer → detenerse y preguntar.
- Si no hay tests → notificarlo (no bloquear, pero registrar).
"