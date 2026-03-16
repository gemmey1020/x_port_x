---
skill_id: yeet
display_name: Yeet
category: automation
status: active
source_skill_path: /home/gemmey1020/.codex/skills/yeet/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Yeet

## Summary
Runs a single GitHub CLI flow that stages, commits, pushes, and opens a pull request when explicitly requested.

## Use When
- Use only when the user explicitly asks for a full stage/commit/push/PR flow.
- Use when GitHub CLI is the intended toolchain.

## Do Not Use When
- Do not use without an explicit request for the full flow.
- Do not use if GitHub CLI is missing or not authenticated.

## Role In Omega Workspace
- Documents the external Git and GitHub PR automation workflow without embedding it into the runtime.

## Inputs And Preconditions
- Requires `gh` to be installed and authenticated.
- Requires a commit description and a usable git repository state.

## Outputs And Effects
- Produces a committed branch, pushed changes, and a draft pull request.

## Constraints And Non-Goals
- Explicit-request only.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/yeet/SKILL.md`

## Notes
- The source skill defines branch, commit, and PR naming conventions.
