---
skill_id: seo-artifact-generator
display_name: SEO Artifact Generator
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/seo-artifact-generator/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# SEO Artifact Generator

## Summary
Generates a deterministic `seo_artifact` from validated downstream pipeline state without generating page copy, HTML, or external SEO intelligence.

## Use When
- Use when a validated trade brief plus downstream portfolio, schema, JSON-LD, and landing outputs must be converted into an SEO handoff artifact.
- Use when metadata, heading plans, locality targeting, and SEO gaps must stay evidence-driven and deterministic.

## Do Not Use When
- Do not use when required structural evidence is missing or invalid.
- Do not use to generate marketing copy, keyword research, or invented SEO claims.

## Role In Omega Workspace
- Documents the structured SEO handoff stage that follows the landing artifact in the workspace pipeline.

## Inputs And Preconditions
- Requires `trade_brief`, `portfolio_output`, `schema_mapping_output`, `jsonld_output`, and `landing_output`.
- Requires source review against `references/seo-rules.md`.

## Outputs And Effects
- Produces a compact `seo_artifact` payload plus source-evidence and implementation-handoff data.

## Constraints And Non-Goals
- Deterministic only; no invented identity, locality, service, or trust fields.
- Blocks with `Ω_INSUFFICIENT_DATA` semantics when required structural evidence is missing.
- SEO artifact only; no HTML or prose generation.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/seo-artifact-generator/SKILL.md`
- `/home/gemmey1020/.codex/skills/seo-artifact-generator/references/seo-rules.md`

## Notes
- The source skill keeps locality handling exact and derives explicit SEO gaps instead of filling them.
