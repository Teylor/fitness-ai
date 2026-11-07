"# Skill: sdd-specify

> Escribe `specs/<feature>/spec.md`: qué y por qué, sin tecnologías.

## Cuándo se activa
Cuando `classify` escala a SDD.

## Pasos

1. **Crear** `specs/<feature-name>/spec.md`.
2. **Escribir**:
   - **Problema**: ¿Qué problema resuelve?
   - **Contexto**: ¿Por qué ahora? ¿Qué limita la solución actual?
   - **Criterios de aceptación**: Lista checkeable (sin tecnología).
   - **No-requirements**: Qué NO se va a hacer (para evitar scope creep).
   - **Supuestos**: Lo que se da por cierto.
3. **No incluir**: tecnologías, frameworks, estructura de archivos, APIs específicas.
4. **Confirmar** al usuario: "Spec escrita. ¿Aprobado?"

## Plantilla

```markdown
# Spec: <feature name>

## Problema
> Qué problema resuelve (sin tecnología)

## Contexto
> Por qué ahora, qué limita la solución actual

## Criterios de aceptación
- [ ] CA1: ...
- [ ] CA2: ...

## No-requirements
- No se va a hacer X
- No se va a hacer Y

## Supuestos
- A1: ...
- A2: ...
```

## Reglas
- Sin tecnología. Si mencionas "SQLite" o "Peewee" → mal.
- El spec es inmutable una vez aprobado (cambios → editar spec → regenerar plan).
- El spec NUNCA guarda estado de progreso.
"