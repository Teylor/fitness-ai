"# Skill: sdd-tasks

> Convierte el plan en checklist dentro del documento ODD, no en un tasks.md aparte.

## Cuándo se activa
Después de `sdd-plan` (plan aprobado por usuario).

## Pasos

1. **Leer** `specs/<feature>/plan.md` y `specs/<feature>/spec.md`.
2. **Descomponer** el plan en tareas pequeñas (cada una < 30 min de trabajo).
3. **Para cada tarea** definir:
   - Descripción clara (qué hacer).
   - Archivo(s) afectado(s).
   - Verificación: test específico, comando, o inspección manual.
   - Dependencias: qué tareas deben estar hechas antes.
4. **Escribir** en `odd/tasks/<feature>.md` sección `## Tasks`:
   ```
   - [ ] T1: <descripción> → files: <paths> → verify: <test/comando>
   - [ ] T2: <descripción> → files: <paths> → verify: <test/comando>
   ```
5. **Enlazar** en el documento ODD:
   ```
   > Spec: [specs/<feature>/spec.md](../../specs/<feature>/spec.md)
   > Plan: [specs/<feature>/plan.md](../../specs/<feature>/plan.md)
   ```
6. **Confirmar** al usuario: "Checklist de N tareas creado. ¿Aprobado para implementar?"

## Reglas
- **No crear un tasks.md aparte.** El checklist vive en `odd/tasks/<feature>.md`.
- Cada tarea debe ser independiente (o declarar dependencia explícita).
- Cada tarea debe tener verificación. Sin verificación → no es una tarea válida.
- Ordenar tareas por dependencia (lo que se usa antes va primero).
- Si una tarea es > 30 min → descomponer más.
- Incluir tarea final: "Ejecutar test suite completo" → verify: `pytest tests/ -v`
"