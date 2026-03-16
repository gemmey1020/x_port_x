---
skill_id: sentry
display_name: Sentry
category: observability
status: active
source_skill_path: /home/gemmey1020/.codex/skills/sentry/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Sentry

## Summary
Documents a portable Sentry workspace capability that starts with foundation checks and later supports integration and read-only operations.

## Use When
- Use when Sentry capability setup, validation, integration planning, or later live inspection is needed.
- Use when the work should begin from foundation readiness rather than immediate live operations.

## Do Not Use When
- Do not use as a write-capable incident management tool.
- Do not skip readiness gates before operational use.

## Role In Omega Workspace
- Documents the external Sentry capability as a workspace-layer observability reference.

## Inputs And Preconditions
- Foundation and integration expectations come from the external skill.
- Live operations require the external readiness gates defined by the source skill.

## Outputs And Effects
- Supports foundation validation, integration contracts, and later read-only operational querying.

## Constraints And Non-Goals
- Documentation only in this domain.
- External implementation remains the source of behavior and gating.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/sentry/SKILL.md`
- `/home/gemmey1020/.codex/skills/sentry/scripts/sentry_api.py`

## Notes
- The source skill is layered as Foundation, Integration, and Operations.
