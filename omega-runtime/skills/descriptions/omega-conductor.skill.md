---
skill_id: omega-conductor
display_name: Omega Conductor
category: planning
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-conductor/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega Conductor

## Summary
Turns an approved plan into a safe execution graph by deciding single-agent vs multi-agent execution, assigning ownership, defining sync points, and preparing proof handoff.

## Use When
- Use when planning and critique are already complete and the next problem is execution coordination.
- Use when sub-agent work, ownership, integration order, or execution readiness need to be made explicit.

## Do Not Use When
- Do not use for initial planning, plan critique, or repository discovery.
- Do not use for final proof selection or closeout claims.

## Role In Omega Workspace
- Documents the execution-orchestration skill that sits between approved planning and final proof.

## Inputs And Preconditions
- Requires an approved plan or approved bounded-repair plan plus a critic verdict that allows execution.
- Assumes the main unresolved question is coordination, not strategy.

## Outputs And Effects
- Produces execution readiness, work graph, agent allocation, ownership map, sync points, escalation rules, integration order, and proof handoff.

## Constraints And Non-Goals
- Does not rewrite the plan.
- Does not replace `god-plan-critic` or `omega-proof-lock`.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-conductor/SKILL.md`
- `/home/gemmey1020/.codex/skills/omega-conductor/references/execution-modes.md`
- `/home/gemmey1020/.codex/skills/omega-conductor/references/proof-handoff.md`

## Notes
- The source skill explicitly decides whether orchestration is needed at all before allocating any sub-agents.
- Public/operator name: `Omega Conductor`; invoke now with `$omega-conductor`.
