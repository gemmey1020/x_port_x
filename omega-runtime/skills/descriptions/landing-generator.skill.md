---
skill_id: landing-generator
display_name: Landing Generator
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/landing-generator/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Landing Generator

## Summary
Generates a deterministic `landing_artifact` from validated downstream pipeline state without producing HTML, CSS, or components.

## Use When
- Use when a validated trade brief and downstream portfolio, schema, and JSON-LD outputs must be converted into a renderer-safe landing artifact.
- Use when output must remain structured, slot-based, and mobile-first for Arabic-first portfolio work.

## Do Not Use When
- Do not use when required structural inputs are missing or invalid.
- Do not use to generate HTML, CSS, JavaScript, Blade, React, or assembled marketing copy.

## Role In Omega Workspace
- Documents the structured landing handoff stage in the workspace pipeline.

## Inputs And Preconditions
- Requires `trade_brief`, `portfolio_output`, `schema_mapping_output`, and `jsonld_output`.
- Requires source review against `references/landing-rules.md`.

## Outputs And Effects
- Produces a compact `landing_artifact` payload plus missing-input and implementation-handoff data.

## Constraints And Non-Goals
- Deterministic only; no invented sections or slot values.
- Blocks with `Ω_INSUFFICIENT_DATA` semantics when required structural evidence is missing.
- Renderer-safe payload only; no page-builder logic.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/landing-generator/SKILL.md`
- `/home/gemmey1020/.codex/skills/landing-generator/references/landing-rules.md`

## Notes
- The source skill keeps JSON-LD attached verbatim and preserves the upstream section order.
