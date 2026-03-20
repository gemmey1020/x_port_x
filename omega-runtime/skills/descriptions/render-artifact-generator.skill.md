---
skill_id: render-artifact-generator
display_name: Render Artifact Generator
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/render-artifact-generator/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Render Artifact Generator

## Summary
Converts validated downstream renderer state into one deterministic `render_artifact` without generating HTML, CSS, or invented content.

## Use When
- Use when validated `landing_output`, `seo_output`, and `jsonld_output` are ready for renderer-safe packaging.
- Use when the downstream pipeline needs deterministic render state instead of authored UI code.

## Do Not Use When
- Do not use if required upstream structural evidence is missing or invalid.
- Do not use for direct HTML, CSS, framework, or copy generation.

## Role In Omega Workspace
- Documents the deterministic renderer-state packaging step inside the structured-output pipeline.

## Inputs And Preconditions
- Requires `landing_output`, `seo_output`, and `jsonld_output` with matching emitted tiers.
- Requires strict upstream validation before emission.

## Outputs And Effects
- Produces a compact `render_artifact` payload or returns `Ω_INSUFFICIENT_DATA`.

## Constraints And Non-Goals
- Does not invent values, headings, CTA logic, or fallback content.
- Does not act as a renderer or HTML author.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/render-artifact-generator/SKILL.md`

## Notes
- This skill is structural and deterministic, not presentational.
