---
skill_id: persistent-memory
display_name: Persistent Memory
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/persistent-memory/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Persistent Memory

## Summary
Manages a local-only durable memory layer for Codex with inspect, triage, backfill, promotion, rejection, forgetting, and rollback flows.

## Use When
- Use when current durable memory must be inspected before work.
- Use when pending memory candidates must be grouped into promotable, ephemeral, and conflicting sets.
- Use when explicit memory promotion, rejection, forgetting, or rollback is required.

## Do Not Use When
- Do not use for automatic learning or silent promotion.
- Do not use to write into Codex internals such as `state_5.sqlite` or session transcript files.

## Role In Omega Workspace
- Documents the external cross-workspace memory capability used to preserve durable user and project context.

## Inputs And Preconditions
- Requires a healthy memory store under `~/.codex/memory`.
- Uses the current workspace path to resolve project overlays.
- May reindex local transcripts only when the operator explicitly requests backfill.

## Outputs And Effects
- Produces inspect, triage, and suggest views of memory state.
- May apply explicit durable-memory mutations in the external memory store.

## Constraints And Non-Goals
- Local-only and deterministic by design.
- Promotion remains explicit.
- In v1, `project.active_artifact` and `project.root_fact` are ephemeral and non-promotable.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/persistent-memory/SKILL.md`
- `/home/gemmey1020/.codex/skills/persistent-memory/scripts/memory_cli.py`

## Notes
- The source skill now prefers `triage` as the operator-facing grouped view over raw `suggest`.
