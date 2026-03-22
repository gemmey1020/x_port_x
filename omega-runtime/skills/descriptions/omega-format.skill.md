---
skill_id: omega-format
display_name: Omega Format
category: system
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-format/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega Format

## Summary
Applies a conservative formatting layer to user-facing replies while preserving exact-structure content such as code, JSON, patches, commands, and plan blocks.

## Use When
- Use when a drafted reply needs consistent presentation across Arabic, English, or mixed output.
- Use when formatting must stay markdown-safe and structure-aware.

## Do Not Use When
- Do not use to invent, expand, or semantically rewrite the actual answer.
- Do not use on protected exact-structure payloads that should bypass formatting.

## Role In Omega Workspace
- Documents the external reply-formatting layer that standardizes presentation without becoming a content-generation path.

## Inputs And Preconditions
- Requires a drafted user-facing reply and a need to classify reply kind or surface policy.
- Assumes protected spans such as code, identifiers, and URLs must remain byte-stable.

## Outputs And Effects
- Produces presentation-only formatting decisions or markdown-safe output adjustments.

## Constraints And Non-Goals
- Formatting only; no meaning drift, content invention, or order changes when order carries meaning.
- HTML remains gated and non-default.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-format/SKILL.md`
- `/home/gemmey1020/.codex/skills/omega-format/scripts/apply_omega_format.py`

## Notes
- The source skill explicitly bypasses `<proposed_plan>` payloads and other exact-structure responses.
