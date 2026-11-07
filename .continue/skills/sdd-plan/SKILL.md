"# Skill: sdd-plan

> Escribe `specs/<feature>/plan.md`: arquitectura, decisiones y riesgos, alineado con la constitución.

## Cuándo se activa
Después de `sdd-clarify` (todas las ambigüedades resueltas).

## Pasos

1. **Crear** `specs/<feature>/plan.md`.
2. **Escribir**:
   - **Arquitectura**: Componentes afectados, nuevos, interacciones.
   - **Decisiones técnicas**: Qué librerías, patrones, estructura.
   - **ADR nuevos**: Si hay decisiones que afectan a todo el proyecto → registrar en `docs/architecture/ssd-decisions.md`.
   - **Riesgos**: Qué puede salir mal y mitigación.
   - **Dependencias**: Qué debe existir antes, qué bloquea.
   - **Migraciones**: Si hay cambios de DB → script SQL / Peewee migration.
3. **Alinear** con ADRs existentes (no contradecir sin justificar).
4. **Confirmar** al usuario: "Plan escrito. ¿Aprobado?"

## Plantilla

```markdown
# Plan: <feature name>

## Arquitectura
> Componentes afectados y nuevos

## Decisiones técnicas
- D1: ...
- D2: ...

## ADRs nuevos
- ADR-XXX: ... (o "Ninguno")

## Riesgos
| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| ... | ... | ... |

## Dependencias
- Debe existir antes: ...
- Bloquea: ...

## Migraciones
- [ ] 00X_<name>.sql
- [ ] peewee-migrate create <name>

## Alineación con ADRs existentes
- ADR-001: ✅ Compatible
- ADR-003: ⚠️ Afecta (explicar)
```

## Reglas
- No contradecir ADRs existentes sin crear un ADR nuevo que los supere.
- Si el plan requiere cambiar una tool MCP existente → notificar (cambia contrato público).
- El plan es inmutable una vez aprobado (cambios → editar → re-planificar tareas afectadas).
"