"# Skill: sdd-clarify

> Lista ambigüedades y las resuelve antes de seguir.

## Cuándo se activa
Después de `sdd-specify`, antes de `sdd-plan`.

## Pasos

1. **Leer** `specs/<feature>/spec.md`.
2. **Listar** todas las ambigüedades, supuestos no explícitos, preguntas sin responder:
   - ¿Qué pasa si...?
   - ¿Y si el usuario...?
   - ¿Qué significa exactamente...?
   - ¿Hay algún límite o restricción no documentada?
3. **Presentar** al usuario en formato P/R:
   ```
   P1: ¿...? → R: (pendiente)
   P2: ¿...? → R: (pendiente)
   ```
4. **Resolver** cada una con el usuario.
5. **Actualizar** `odd/tasks/<feature>.md` sección `## Clarify` con las respuestas.
6. **Si una respuesta cambia el spec** → actualizar `spec.md` primero.

## Reglas
- No pasar a `sdd-plan` con ambigüedades sin resolver.
- Si el usuario dice "no lo sé" → proponer una opción y registrarla como supuesto.
- Máximo 2 rondas de clarify. Si hay más de 5 preguntas → el spec está mal escrito, volver a `sdd-specify`.
"