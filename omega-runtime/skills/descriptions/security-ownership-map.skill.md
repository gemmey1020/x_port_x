---
skill_id: security-ownership-map
display_name: Security Ownership Map
category: security
status: active
source_skill_path: /home/gemmey1020/.codex/skills/security-ownership-map/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Security Ownership Map

## Summary
Analyzes repositories to build a security ownership topology and related risk outputs.

## Use When
- Use when a security-oriented ownership or bus-factor analysis is explicitly requested.
- Use when the answer must be grounded in repository history.

## Do Not Use When
- Do not use for general maintainer lists.
- Do not use for non-security ownership questions.

## Role In Omega Workspace
- Documents an external security-analysis capability relevant to repository governance work.

## Inputs And Preconditions
- Requires a git repository and a security-oriented ownership question.

## Outputs And Effects
- Produces ownership topology outputs and related CSV or JSON artifacts.

## Constraints And Non-Goals
- Security-focused only.
- Not a generic repository summary tool.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/security-ownership-map/SKILL.md`

## Notes
- The source skill is grounded in git history rather than static assumptions.
