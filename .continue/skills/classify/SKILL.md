# Skill: classify

> Decide el tamaño del cambio: trivial, pequeño, sustancial o necesita SDD.

## Cuándo se activa
Después de `explore`, antes de `track-feature`.

## Criterios

| Tamaño | Criterios | Acción |
|--------|-----------|--------|
| **Trivial** | 1 archivo, typo, rename, config, comentario | → `track-feature` (mínimo) → `implement-task` → `close` |
| **Pequeño** | 1-2 archivos, 1 módulo, sin API pública, sin migración | → `track-feature` → `implement-task` → `close` |
| **Sustancial** | Varios módulos, nueva entidad, nueva tool MCP, nueva tabla | → `track-feature` (con spec inline) → `implement-task` → `close` |
| **Necesita SDD** | Cambia contrato público/API, migración de datos, seguridad, difícil de revertir, varios agentes en paralelo, requisitos ambiguos | → `sdd-specify` → `sdd-clarify` → `sdd-plan` → `sdd-tasks` → `track-feature` → `implement-task` → `close` |

## Criterios de escalado a SDD (cualquiera de estos):
- Cambia un contrato público o API (tool MCP)
- Toca varios módulos simultáneamente
- Los requisitos son ambiguos o hay múltiples interpretaciones
- Afecta a seguridad o migración de datos
- Es difícil de revertir
- Varios agentes trabajarán en paralelo

## Salida
- Decisión documentada en `odd/tasks/<feature>.md` (sección "Plan" → "Clasificación").
- Si escala a SDD → invocar `sdd-specify`.

## Reglas
- Ante la duda, escalar un nivel.
- Si durante `implement-task` aparece complejidad inesperada → reclasificar y escalar.
- Registrar el motivo de la clasificación.