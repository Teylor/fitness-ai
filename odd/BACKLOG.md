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
8. Each feature is developed on its own branch `feat/<feature-name>`, created when the feature starts. A fix to a feature is made on a `fix/<feature-name>` branch. When a feature is closed, after the last commit, push the branch and create a Pull Request to `main` directly.

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
| 7 | P2 | `db-robustness` | ✅ Approved | Rollback in `get_db()` (pending db-layer close). |
| 8 | P3 | `seed-data` | ✅ Approved | Initial catalog of ingredients/exercises. |
| 9 | P2 | `odd-merge-back` | ✅ Approved | When closing, reflux the met criteria to global `docs/specs/` (mimics OpenSpec's delta merge; closes the ODD's weak point). |
| 10 | P2 | `google-health-api` | 📥 Proposed | Connect Google Health API to sync and add meals. |

> Recommended execution order: `mcp-server` (12 nutrition & goal tools) → `services-training` (training services + 6 MCP tools) → `hermes-e2e`. `specs-completion` can run in parallel.

---

## ➡️ In progress

| Feature | File |
|---------|---------|
| `html-artifacts` | `odd/tasks/html-artifacts.md` |

---

## 🏁 Done

| Feature | File | Date |
|---------|---------|-------|
| `hermes-e2e` | `odd/tasks/hermes-e2e.md` | 2026-11 |
| `services-training` | `odd/tasks/services-training.md` | 2026-11 |
| `mcp-server` | `odd/tasks/mcp-server.md` | 2026-11 |
| `services-nutrition` | `odd/tasks/services-nutrition.md` | 2026-11 |
| `specs-completion` | `odd/tasks/specs-completion.md` | 2026-11 |
| db-layer | `odd/tasks/db-layer.md` | 2026-11 |
| utils-core | `odd/tasks/utils-core.md` | 2026-11 |
| translate-to-english | `odd/tasks/translate-to-english.md` | 2026-11 |

---

## ❌ Dropped

| Feature | Reason |
|---------|--------|
| — | — |
