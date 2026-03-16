---
skill_id: plan-critic
display_name: Plan Critic
category: planning
status: active
source_skill_path: /home/gemmey1020/.codex/skills/plan-critic/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Plan Critic

## Summary
Reviews execution plans to identify high-impact weaknesses before work begins.

## Use When
- Use when a draft plan already exists and needs a strict review.
- Use when sequencing, dependencies, verification, or scope need challenge.

## Do Not Use When
- Do not use when there is no meaningful plan artifact to critique.
- Do not use for trivial direct execution requests.

## Role In Omega Workspace
- Documents the plan-review path used to tighten multi-step implementation plans.

## Inputs And Preconditions
- Requires an existing plan, implementation strategy, or multi-step proposal.

## Outputs And Effects
- Produces findings-first critique and may provide a bounded repaired plan.

## Constraints And Non-Goals
- Should focus on execution quality, not style.
- Not a replacement for implementation.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/plan-critic/SKILL.md`

## Notes
- The source skill ranks findings by execution impact.
