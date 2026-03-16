---
skill_id: pdf
display_name: PDF Skill
category: io
status: active
source_skill_path: /home/gemmey1020/.codex/skills/pdf/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# PDF Skill

## Summary
Handles PDF reading, creation, and review when rendering and page layout matter.

## Use When
- Use for PDF extraction, generation, or layout-sensitive review.
- Use when rendered page inspection is part of the task.

## Do Not Use When
- Do not use for non-PDF document tasks.
- Do not treat text extraction alone as sufficient when layout is important.

## Role In Omega Workspace
- Documents the external PDF workflow as a reusable workspace reference.

## Inputs And Preconditions
- Requires a PDF task or source file.
- Assumes the external PDF toolchain is available.

## Outputs And Effects
- Produces or inspects PDF artifacts with rendering-aware validation.

## Constraints And Non-Goals
- Focused on PDF workflows only.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/pdf/SKILL.md`

## Notes
- The source skill prefers visual validation when page fidelity matters.
