---
skill_id: omega-html
display_name: Omega HTML
category: io
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-html/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega HTML

## Summary
Generates one printable Omega-branded HTML report artifact intended to become the source of truth for downstream PDF export.

## Use When
- Use when the user wants a print-first Omega report in HTML.
- Use when the HTML artifact must be ready for downstream `pdf` export.

## Do Not Use When
- Do not use for websites, landing pages, generic HTML pages, or PDF QA.
- Do not use for component work or runtime web application authoring.

## Role In Omega Workspace
- Documents the print-grade HTML authoring path that hands off later to the PDF workflow.

## Inputs And Preconditions
- Requires report-oriented content rather than interactive product UI.
- Requires local-only styles, fonts, and deterministic layout decisions.

## Outputs And Effects
- Produces a single print-safe HTML artifact with Omega layout and handoff metadata.

## Constraints And Non-Goals
- No remote CSS, CDN fonts, or runtime JS dependencies.
- Does not own the later PDF export or PDF QA step.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-html/SKILL.md`

## Notes
- This is a report artifact path, not a website-generation path.
