---
skill_id: omega-proof-gate
display_name: Omega Proof Gate
category: planning
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-proof-gate/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega Proof Gate

## Summary
Selects the smallest honest proof package for completed work by choosing the strongest realistic checks and separating ran, not-run, blocked, and residual-risk states.

## Use When
- Use when implementation, debugging, or review work is mostly done and needs defensible validation.
- Use when the task needs proof selection and an honest closeout rather than more discovery.

## Do Not Use When
- Do not use as a replacement for repo exploration or runtime design.
- Do not use to inflate confidence without naming concrete checks.

## Role In Omega Workspace
- Documents the external validation-and-closeout skill that turns vague “tested” claims into explicit proof coverage.

## Inputs And Preconditions
- Requires a known change path or review target and enough repo context to evaluate relevant checks.
- Assumes the goal is evidence packaging, not feature design.

## Outputs And Effects
- Produces a proof plan, check inventory, execution ledger, manual coverage notes, and residual-risk framing.

## Constraints And Non-Goals
- Prefers minimum convincing proof over exhaustive test theater.
- Keeps unexplored code paths and blocked checks explicit instead of hidden.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-proof-gate/SKILL.md`
- `/home/gemmey1020/.codex/skills/omega-proof-gate/scripts/discover_checks.py`

## Notes
- The source skill explicitly distinguishes `Ran`, `Manual`, `Not Run`, `Blocked`, and `Residual Risk`.
