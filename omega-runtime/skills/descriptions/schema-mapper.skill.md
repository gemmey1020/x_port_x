---
skill_id: schema-mapper
display_name: Schema Mapper
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/schema-mapper/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Schema Mapper

## Summary
Maps a validated `portfolio_spectrum` payload into schema-ready mapping targets without generating JSON-LD.

## Use When
- Use when an approved `portfolio_spectrum` payload must be converted into deterministic schema mappings.
- Use when upstream evidence and implementation handoff fields are already available.

## Do Not Use When
- Do not use when required upstream evidence is missing or invalid.
- Do not use to generate JSON-LD or invent schema fields.

## Role In Omega Workspace
- Documents a workspace-specific mapping capability that follows upstream portfolio outputs.

## Inputs And Preconditions
- Requires validated `portfolio_spectrum`, `source_evidence`, and `implementation_handoff` objects.

## Outputs And Effects
- Produces a compact `schema_mapping` payload plus missing-field and handoff information.

## Constraints And Non-Goals
- Must block with `Ω_INSUFFICIENT_DATA` semantics when required evidence is missing.
- Mapping only; no JSON-LD generation and no invented values.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/schema-mapper/SKILL.md`
- `/home/gemmey1020/.codex/skills/schema-mapper/references/schema-rules.md`

## Notes
- The source skill is deterministic and evidence-gated.
