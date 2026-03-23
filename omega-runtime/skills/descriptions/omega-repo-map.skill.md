---
skill_id: omega-repo-map
display_name: Omega Third Eye
category: planning
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-repo-map/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega Third Eye

## Summary
Builds a fast, evidence-first map of an unfamiliar repository by identifying stack markers, likely flow paths, entrypoints, and blast radius before editing.

## Use When
- Use when the next useful step depends on locating the right route, entrypoint, feature path, or impact surface.
- Use when a repo is unfamiliar and work should begin with facts instead of assumptions.

## Do Not Use When
- Do not use when the main question is proof selection or AI runtime design.
- Do not use to replace implementation planning once the code path is already known.

## Role In Omega Workspace
- Documents the external repo-discovery skill used to reduce first-contact ambiguity and narrow the edit surface safely.

## Inputs And Preconditions
- Requires a repository-grounded request where locating the right path is part of the work.
- Assumes targeted search and stack detection are more valuable than speculative architecture summaries.

## Outputs And Effects
- Produces `RepoFacts`, `FlowPath`, `ImpactMap`, and explicit unknowns for follow-up work.

## Constraints And Non-Goals
- Discovery-focused only; it does not perform the implementation or the final validation pass.
- Stops once the next likely edit target is obvious instead of narrating the whole repo.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-repo-map/SKILL.md`
- `/home/gemmey1020/.codex/skills/omega-repo-map/scripts/scan_repo_map.py`

## Notes
- The source skill explicitly prefers tracing one strong path first over producing broad speculative maps.
- Public/operator name: `Omega Third Eye`; invoke now with `$omega-repo-map`.
- Internal skill id remains `omega-repo-map`.
