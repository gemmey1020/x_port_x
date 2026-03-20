---
skill_id: figma
display_name: Figma MCP
category: design
status: active
source_skill_path: /home/gemmey1020/.codex/skills/figma/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Figma MCP

## Summary
Provides the Figma MCP workflow for extracting design context, screenshots, variables, and assets before implementation.

## Use When
- Use when the request depends on a Figma URL, node ID, screenshot, asset, or design-to-code translation.
- Use when the implementation must stay grounded in Figma source truth.

## Do Not Use When
- Do not use for purely generative UI work with no Figma source.
- Do not use as a generic styling or redesign skill.

## Role In Omega Workspace
- Documents the Figma-source integration layer used to feed downstream implementation work.

## Inputs And Preconditions
- Requires a working Figma MCP connection and a target node or selection.
- Requires source extraction before any implementation starts.

## Outputs And Effects
- Produces grounded design context, screenshots, and asset references for implementation.

## Constraints And Non-Goals
- Does not replace project conventions or local component systems.
- Does not justify skipping Figma-source verification.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/figma/SKILL.md`

## Notes
- Source extraction should happen before any premium refinement or design-system cleanup.
