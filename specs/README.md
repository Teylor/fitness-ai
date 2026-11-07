# Specs (SDD)

> Especificaciones de features que escalan a SDD. Solo se crean cuando `classify` lo decide.

## Estructura

```
specs/
├── README.md              ← este archivo
├── <feature-1>/
│   ├── spec.md           # Qué y por qué (sin tecnología)
│   └── plan.md           # Decisiones técnicas
├── <feature-2>/
│   ├── spec.md
│   └── plan.md
└── _archive/             # Specs implementados y archivados
    └── <feature-old>/
        ├── spec.md
        └── plan.md
```

## Reglas

1. El spec NUNCA guarda estado de progreso (eso vive en `odd/tasks/<feature>.md`).
2. El spec es inmutable una vez aprobado. Cambios → editar → regenerar plan.
3. Al cerrar → `sdd-archive` lo mueve a `_archive/`.
4. Si se necesita reabrir → nueva feature, no se reabre el archivado.
