"# Skill: track-feature

> Crea o actualiza `odd/tasks/<feature>.md` antes de la primera escritura de código.

## Cuándo se activa
Después de `classify` (o `sdd-tasks` si escaló a SDD), antes de `implement-task`.

## Pasos

1. **Crear archivo** `odd/tasks/<feature-name>.md` si no existe.
2. **Rellenar secciones**:
   - `## Spec` → Qué y por qué (criterios de aceptación)
   - `## Clarify` → Ambigüedades resueltas (P/R)
   - `## Plan` → Decisiones técnicas + clasificación
   - `## Tasks` → Checklist con verificación por tarea
   - `## Verification` → (vacío, se rellena al cerrar)
   - `## Close` → (vacío, se rellena al cerrar)
3. **Enlazar** a `specs/<feature>/spec.md` y `plan.md` si existen (rama SDD).
4. **Confirmar** al usuario: "Checklist creado. ¿Aprobado para implementar?"

## Plantilla

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
> Decisiones técnicas + clasificación

- Clasificación: <trivial|pequeño|sustancial|SDD>
- D1: ...
- D2: ...

## Tasks
> Checklist de implementación

- [ ] T1: <descripción> → verify: <test/comando>
- [ ] T2: <descripción> → verify: <test/comando>

## Verification
> Contraste con spec (se rellena al cerrar)

## Close
> Cierre (se rellena al cerrar)
```

## Reglas
- **Una sola fuente de progreso.** El checklist vive SOLO aquí.
- El spec nunca guarda estado (si existe como archivo separado).
- No se empieza `implement-task` sin este archivo.
- Si el feature ya existe → actualizar, no crear nuevo.
"