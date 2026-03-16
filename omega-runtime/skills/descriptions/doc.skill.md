---
skill_id: doc
display_name: DOCX Skill
category: io
status: active
source_skill_path: /home/gemmey1020/.codex/skills/doc/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# DOCX Skill

## Summary
Handles `.docx` reading, creation, and editing when document structure or layout fidelity matters.

## Use When
- Use for `.docx` creation or editing tasks.
- Use when document formatting needs visual verification.

## Do Not Use When
- Do not use for non-document file types.
- Do not use when plain text output is enough.

## Role In Omega Workspace
- Documents the external DOCX workflow as a reusable workspace capability reference.

## Inputs And Preconditions
- Requires a `.docx` task or source document.
- Assumes `python-docx` and the source render helper are available externally.

## Outputs And Effects
- Produces or updates `.docx` documents.
- Supports layout-aware review flows.

## Constraints And Non-Goals
- Focused on DOCX workflows only.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/doc/SKILL.md`
- `/home/gemmey1020/.codex/skills/doc/scripts/render_docx.py`

## Notes
- The source skill prefers visual checks when formatting fidelity matters.
