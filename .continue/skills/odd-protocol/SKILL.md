# Skill: odd-protocol

> Orquestador del ciclo ODD. Impone el orden: autorizar, explorar, resolver incertidumbre, clasificar, registrar, implementar, cerrar.

## Cuándo se activa
Siempre. Es el primer skill que se invoca ante cualquier petición de cambio.

## Pasos

1. **Autorizar**: Confirmar con el usuario que se va a trabajar en la feature.
2. **Explorar** (→ `explore`): Leer código real, tests, ADRs relevantes.
3. **Resolver incertidumbre**: Preguntar al usuario lo que no se entiende.
4. **Clasificar** (→ `classify`): Decidir tamaño (trivial/pequeño/sustancial/SDD).
5. **Registrar** (→ `track-feature`): Crear `odd/tasks/<feature>.md`.
6. **Implementar** (→ `implement-task`): Una tarea por vez, TDD, report pre-commit antes de cada commit (el commit lo ejecuta el usuario).
7. **Cerrar** (→ `close-feature`): Verificar criterios, actualizar docs, dejar siguiente paso.

## Reglas
- No saltar pasos.
- No implementar sin `track-feature`.
- No cerrar sin verificar todos los criterios de aceptación.
- No hay commit sin report pre-commit (cambios, tests si aplican, mensaje sugerido) y decisión del usuario.
- El agente no ejecuta `git commit` por su cuenta.
- Si `classify` escala a SDD → invocar rama SDD antes de `implement-task`.
