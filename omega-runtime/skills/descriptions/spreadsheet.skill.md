---
skill_id: spreadsheet
display_name: Spreadsheet Skill
category: io
status: active
source_skill_path: /home/gemmey1020/.codex/skills/spreadsheet/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Spreadsheet Skill

## Summary
Handles spreadsheet creation, editing, analysis, and formatting for `.xlsx`, `.csv`, and `.tsv` workflows.

## Use When
- Use when spreadsheet structure, formulas, references, or formatting matter.
- Use for spreadsheet analysis or transformation work.

## Do Not Use When
- Do not use for non-spreadsheet file types.
- Do not use when plain text tabular output is sufficient.

## Role In Omega Workspace
- Documents the external spreadsheet workflow as a reusable workspace reference.

## Inputs And Preconditions
- Requires spreadsheet files or a spreadsheet-oriented task.
- Assumes the external Python spreadsheet toolchain is available.

## Outputs And Effects
- Produces or updates spreadsheet artifacts while preserving structure-sensitive details.

## Constraints And Non-Goals
- Focused on spreadsheet workflows only.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/spreadsheet/SKILL.md`

## Notes
- The source skill is built around Python spreadsheet tooling rather than manual editing.
