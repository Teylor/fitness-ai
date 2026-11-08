# Feature Tasks (ODD)

> A single source of progress per feature. The checklist lives HERE, not in the spec.

## Structure

```
odd/tasks/
├── README.md              ← this file
├── <feature-1>.md         ← feature 1 checklist
├── <feature-2>.md         ← feature 2 checklist
└── ...
```

## Rules

1. One file per feature.
2. The spec never holds state. Only here.
3. If a feature has an SDD spec → link `specs/<feature>/spec.md` and `plan.md`.
4. Nothing is implemented without this file.
5. The feature item comes from `odd/BACKLOG.md`; when this file is created, the item moves to ➡️ In progress.
6. Each feature is developed on its own branch `feat/<feature-name>`; a fix to a feature is made on a `fix/<feature-name>` branch.
