# Backlog

> Project work queues. A backlog item = a future feature
> that, once approved, becomes `odd/tasks/<feature>.md` (SDD+ODD cycle).

## Rules

1. One item = one feature (no loose tasks).
2. Nothing is implemented without passing through `odd/tasks/<feature>.md` (SPECIFY → CLARIFY → PLAN → TASKS).
3. Items are ordered by priority: `P0` (now) / `P1` (next) / `P2` (later) / `P3` (idea).
4. This file is the only place where new work is proposed.
5. When starting a feature → the item moves to `odd/tasks/<feature>.md` and disappears from Proposed.
6. When closing it (all tasks ✅ + Verification filled in `odd/tasks/<feature>.md`) → update the global specification in `docs/specs/openspec/` if the feature introduced or changed requirements, tools, or data models, and then list the item in **Done** with a date.
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

| Priority | Feature | Description | Reference |
|:---:|---------|-------------|-----------|
| `P1` | `day-off-daily-goals` | Add a "Day Off" toggle for daily nutritional goals to switch between training-day and rest-day targets | — |
| `P3` | `android-apk-remote-access` | Package dashboard into Android APK (Capacitor/PWA) and enable remote API access via Cloudflare Tunnel / Tailscale | [ADR-003](docs/architecture/ssd-decisions.md#adr-003-mobile-access-strategy-android-apk--remote-api) |

---

## ➡️ In progress

| Feature | File |
|---------|---------|

---

## 🏁 Done

| Feature | File | Date |
|---------|---------|-------|
| `ui-favicon` | `odd/tasks/ui-favicon.md` | 2026-11 |
| `google-health-ui-data-mismatch` | `odd/tasks/fix-steps.md` | 2026-11 |
| `sync-optimization` | `odd/tasks/sync-optimization.md` | 2026-11 |
| `fix-steps` | `odd/tasks/fix-steps.md` | 2026-11 |
| `supplements-and-water` | `odd/tasks/supplements-and-water.md` | 2026-11 |
| `ui-exercises-prs` | `odd/tasks/ui-exercises-prs.md` | 2026-11 |
| `meal-types` | `odd/tasks/meal-types.md` | 2026-11 |
| `steps-google-health-pull` | `odd/tasks/steps-google-health-pull.md` | 2026-11 |
| `google-health-autosync` | `odd/tasks/google-health-autosync.md` | 2026-11 |
| `odd-merge-back` | `odd/tasks/odd-merge-back.md` | 2026-11 |
| `db-robustness` | `odd/tasks/db-robustness.md` | 2026-11 |
| `google-health-food-sync` | `odd/tasks/google-health-food-sync.md` | 2026-11 |
| `ui-delete-actions` | `odd/tasks/ui-delete-actions.md` | 2026-11 |
| `ui-full-daily-summary` | `odd/tasks/ui-full-daily-summary.md` | 2026-11 |
| `ui-new-features` | `odd/tasks/ui-new-features.md` | 2026-11 |
| `ui-catalog-and-edit` | `odd/tasks/ui-catalog-and-edit.md` | 2026-11 |
| `google-health-api` | `odd/tasks/google-health-api.md` | 2026-11 |
| `html-artifacts` | `odd/tasks/html-artifacts.md` | 2026-11 |
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
| `seed-data` | Dropped by user preference: catalog will be populated incrementally as consumed via the UI. |
