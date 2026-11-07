# Feature Tasks (ODD)

> Una sola fuente de progreso por feature. El checklist vive AQUÍ, no en el spec.

## Estructura

```
odd/tasks/
├── README.md              ← este archivo
├── <feature-1>.md         ← checklist de feature 1
├── <feature-2>.md         ← checklist de feature 2
└── ...
```

## Reglas

1. Un archivo por feature.
2. El spec nunca guarda estado. Solo aquí.
3. Si una feature tiene spec SDD → enlazar `specs/<feature>/spec.md` y `plan.md`.
4. No se implementa sin este archivo.
5. El item del feature procede de `odd/BACKLOG.md`; al crear este archivo, el item pasa a ➡️ En curso.
