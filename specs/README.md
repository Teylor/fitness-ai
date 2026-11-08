# Specs (SDD)

> Specifications for features that scale to SDD. Only created when `classify` decides so.

## Structure

```
specs/
├── README.md              ← this file
├── <feature-1>/
│   ├── spec.md           # What and why (no technology)
│   └── plan.md           # Technical decisions
├── <feature-2>/
│   ├── spec.md
│   └── plan.md
└── _archive/             # Implemented and archived specs
    └── <feature-old>/
        ├── spec.md
        └── plan.md
```

## Rules

1. The spec NEVER stores progress state (that lives in `odd/tasks/<feature>.md`).
2. The spec is immutable once approved. Changes → edit → regenerate plan.
3. On close → `sdd-archive` moves it to `_archive/`.
4. If a reopen is needed → new feature; the archived one is not reopened.
