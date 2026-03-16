---
skill_id: arabic-output-guard
display_name: Arabic Output Guard
category: system
status: active
source_skill_path: /home/gemmey1020/.codex/skills/.system/arabic-output-guard/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Arabic Output Guard

## Summary
Formats Arabic or mixed Arabic-English final output for generic Codex text surfaces.

## Use When
- Use when the final answer is Arabic-heavy or mixed Arabic and English.
- Use when readability on LTR text surfaces matters.

## Do Not Use When
- Do not use as a content-generation skill by itself.
- Do not use HTML output unless the surface supports HTML and HTML is explicitly requested.

## Role In Omega Workspace
- Provides a documented reference for output-formatting support, while implementation remains external.

## Inputs And Preconditions
- Requires a final draft text.
- Assumes the source formatter script is available in the external skill.

## Outputs And Effects
- Produces a readability-adjusted final draft.
- Preserves code blocks and inline code.

## Constraints And Non-Goals
- Formatting only; it does not change product logic.
- Not a source of execution inside `omega-runtime`.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/.system/arabic-output-guard/SKILL.md`
- Shared formatter dependency referenced by the source skill: `/home/gemmey1020/.codex/skills/self-learn/scripts/format_surface_output.py`

## Notes
- The source skill defaults to markdown-safe output on generic LTR surfaces.
