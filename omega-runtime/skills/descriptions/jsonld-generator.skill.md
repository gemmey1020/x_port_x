---
skill_id: jsonld-generator
display_name: JSON-LD Generator
category: workspace
status: active
source_skill_path: /home/gemmey1020/.codex/skills/jsonld-generator/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# JSON-LD Generator

## Summary
Generates deterministic JSON-LD payloads from a validated `schema_mapping` input for supported service schema targets only.

## Use When
- Use when a validated `schema_mapping` payload must be converted into machine-readable JSON-LD.
- Use when output must stay limited to `LocalBusiness` and `ProfessionalService`.

## Do Not Use When
- Do not use when required mapping evidence is missing or invalid.
- Do not use to generate landing-page output, SEO commentary, or invented schema values.

## Role In Omega Workspace
- Documents a deterministic downstream generator in the structured portfolio pipeline.

## Inputs And Preconditions
- Requires `schema_mapping`, `missing_required_fields`, `source_evidence`, and `implementation_handoff` objects.
- Requires source review against `references/jsonld-rules.md`.

## Outputs And Effects
- Produces compact `jsonld_payloads` plus missing-field, evidence, and handoff data.

## Constraints And Non-Goals
- Deterministic only; no invented values.
- Blocks with `Ω_INSUFFICIENT_DATA` semantics when required evidence is missing.
- JSON-LD only; no HTML or landing output generation.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/jsonld-generator/SKILL.md`
- `/home/gemmey1020/.codex/skills/jsonld-generator/references/jsonld-rules.md`

## Notes
- The source skill emits only supported targets and keeps the payload compact and machine-readable.
