---
skill_id: skill-installer
display_name: Skill Installer
category: system
status: active
source_skill_path: /home/gemmey1020/.codex/skills/.system/skill-installer/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Skill Installer

## Summary
Installs Codex skills from a curated list or a GitHub repository path into the Codex skills directory.

## Use When
- Use when a skill must be installed into the local Codex environment.
- Use when the request targets curated or repo-based skill installation.

## Do Not Use When
- Do not use for documenting or describing skills only.
- Do not use for arbitrary repository changes outside skill installation.

## Role In Omega Workspace
- Documents the external skill-installation capability available to the workspace owner.

## Inputs And Preconditions
- Requires an installation target such as a curated skill or GitHub repo path.

## Outputs And Effects
- Installs skills into the external Codex skills location.

## Constraints And Non-Goals
- Installation-focused only.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/.system/skill-installer/SKILL.md`

## Notes
- This domain documents the installer; it does not perform installations itself.
