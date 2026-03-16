---
skill_id: security-threat-model
display_name: Security Threat Model
category: security
status: active
source_skill_path: /home/gemmey1020/.codex/skills/security-threat-model/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Security Threat Model

## Summary
Builds a repository-grounded threat model covering assets, trust boundaries, abuse paths, and mitigations.

## Use When
- Use when the request explicitly asks for threat modeling.
- Use when threats or abuse paths must be analyzed from a repository or path.

## Do Not Use When
- Do not use for general architecture summaries.
- Do not use for non-security design work.

## Role In Omega Workspace
- Documents an external AppSec modeling capability for security-focused repository work.

## Inputs And Preconditions
- Requires a codebase or path and an explicit threat-modeling request.

## Outputs And Effects
- Produces a concise Markdown threat model grounded in repository evidence.

## Constraints And Non-Goals
- Security-focused only.
- Not a generic review or architecture-summary tool.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/security-threat-model/SKILL.md`

## Notes
- The source skill is intended for repository-grounded AppSec analysis.
