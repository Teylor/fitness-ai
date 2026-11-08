# Backlog

> Project work queues. A backlog item = a future feature
> that, once approved, becomes `odd/tasks/<feature>.md` (SDD+ODD cycle).

## Rules

1. One item = one feature (no loose tasks).
2. Nothing is implemented without passing through `odd/tasks/<feature>.md` (SPECIFY → CLARIFY → PLAN → TASKS).
3. Items are ordered by priority: `P0` (now) / `P1` (next) / `P2` (later) / `P3` (idea).
4. This file is the only place where new work is proposed.
5. When starting a feature → the item moves to `odd/tasks/<feature>.md` and disappears from Proposed.
6. When closing it (all tasks ✅ + Verification filled in `odd/tasks/<feature>.md`) → it is listed in **Done** with a date.
7. The agent keeps the backlog up to date: when a feature starts its item moves to ➡️ In progress; when it closes, to 🏁 Done. The backlog is the single work queue: nothing is started that is not approved here.
8. Each feature is developed on its own branch `feat/<feature-name>`, created when the feature starts. A fix to a feature is made on a `fix/<feature-name>` branch.

## States

| State | Meaning |
|--------|-------------|
| 📥 Proposed | Pending review with the user |
| ✅ Approved | Reviewed and approved; ready for SPECIFY |
| ➡️ In progress | Already has `odd/tasks/<feature>.md` |
| 🏁 Done | Closed: all tasks ✅ and Verification filled in `odd/tasks/<feature>.md` |
| ❌ Dropped | Reviewed and dropped (leave a note of why) |

---

## 📥 Proposed

> Filled after review with the user. Empty = nothing pending.

| # | Priority | Feature | State | Note |
|---|-----------|---------|--------|------|
| 4 | P1 | `services-training` | ✅ Approved | Exercise, Workout (services, sets, PRs, estimated 1RM) + 6 MCP tools (exercise & workout) + tests. |
| 5 | P1 | `specs-completion` | ✅ Approved | Fill `requirements.md`, `api-spec.md` (cut off at line 21), `data-model.md` (empty). |
| 6 | P1 | `hermes-e2e` | ✅ Approved | End-to-end verification with a real MCP client (Hermes). |
| 7 | P2 | `db-robustness` | ✅ Approved | Rollback in `get_db()` (pending db-layer close). |
| 8 | P3 | `seed-data` | ✅ Approved | Initial catalog of ingredients/exercises. |
| 9 | P2 | `odd-merge-back` | ✅ Approved | When closing, reflux the met criteria to global `docs/specs/` (mimics OpenSpec's delta merge; closes the ODD's weak point). |

> Recommended execution order: `mcp-server` (12 nutrition & goal tools) → `services-training` (training services + 6 MCP tools) → `hermes-e2e`. `specs-completion` can run in parallel.

---

## ➡️ In progress

| Feature | File |
|---------|---------|
| `mcp-server` | `odd/tasks/mcp-server.md` |

---

## 🏁 Done

| Feature | File | Date |
|---------|---------|-------|
| `services-nutrition` | `odd/tasks/services-nutrition.md` | 2026-11 |
| db-layer | `odd/tasks/db-layer.md` | 2026-11 |
| utils-core | `odd/tasks/utils-core.md` | 2026-11 |
| translate-to-english | `odd/tasks/translate-to-english.md` | 2026-11 |

---

## ❌ Dropped

| Feature | Reason |
|---------|--------|
| — | — |
