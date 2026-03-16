---
skill_id: self-learn
display_name: Self Learn
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/self-learn/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Self Learn

## Summary
Provides deterministic self-only skill hardening within the `self-learn` skill directory.

## Use When
- Use only for bounded improvement work inside the external `self-learn` skill itself.
- Use when observe, propose, apply, report, or rollback must stay local to that skill.

## Do Not Use When
- Do not use to mutate other skills.
- Do not use as governance or mutation infrastructure for `omega-runtime/skills/`.

## Role In Omega Workspace
- Documents a self-contained external capability and explicitly preserves its self-only boundary.

## Inputs And Preconditions
- Requires work scoped to `/home/gemmey1020/.codex/skills/self-learn`.
- Requires compliance with the source skill mutation policy.

## Outputs And Effects
- Produces self-scoped observations, proposals, bounded applies, reports, or rollbacks.

## Constraints And Non-Goals
- Self-only, local-only, explicit-only.
- Not a workspace-wide mutation engine.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/self-learn/SKILL.md`

## Notes
- This description exists for reference only and does not grant cross-skill mutation authority.
