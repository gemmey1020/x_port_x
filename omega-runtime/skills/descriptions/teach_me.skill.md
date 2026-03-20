---
skill_id: teach_me
display_name: Teach Me
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/teach_me/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Teach Me

## Summary
Explains concrete repository or session artifacts in an evidence-first way when understanding is the primary goal.

## Use When
- Use when the user wants to understand code, logs, diffs, configs, request flow, or grounded architecture.
- Use when explicit teaching intent is stronger than implementation intent.

## Do Not Use When
- Do not use for implementation-first tasks, patching, or generic summarization.
- Do not use for pure theory that is not grounded in the current repo or session.

## Role In Omega Workspace
- Documents the understanding-first explanation path for concrete technical artifacts.

## Inputs And Preconditions
- Requires concrete local evidence such as files, logs, output, or diffs.
- Works best when the scope is a specific artifact rather than a broad abstract topic.

## Outputs And Effects
- Produces grounded explanations, walkthroughs, and educational breakdowns tied to observed evidence.

## Constraints And Non-Goals
- Does not silently drift into code-writing as the main task.
- Does not replace implementation or review workflows.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/teach_me/SKILL.md`

## Notes
- Mixed explanation-plus-implementation requests still remain explanation-first while this skill is active.
