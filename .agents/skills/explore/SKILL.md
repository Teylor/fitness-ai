---
name: explore
description: >-
  Read the actual code, tests, and relevant ADRs before proposing anything.
  Use after authorizing a feature and before classifying it.
---

# Skill: explore

> Read the actual code, tests, and relevant ADRs before proposing anything.

## When it activates
After authorizing, before classifying.

## Steps

1. **Read relevant code**:
   - `src/` → files the feature touches or might touch.
   - `tests/` → existing tests covering that area.
   - `docs/architecture/ssd-decisions.md` → ADRs affecting the decision.
   - `docs/design/odd-models.md` → existing entities.
   - `docs/specs/openspec/api-spec.md` → existing MCP tools.

2. **Identify**:
   - What already exists? (do not reinvent)
   - What patterns are used? (consistency)
   - Which ADRs apply? (do not contradict prior decisions)
   - Which tests cover the area? (do not break what works)

3. **Summarize** for the user:
   - "I reviewed X, Y, Z. This is what already exists. This is what is missing."

## Rules
- Do not propose changes without having read the affected code.
- If an ADR contradicts what is being done → stop and ask.
- If there are no tests → report it (do not block, but record it).
