---
skill_id: vercel-deploy
display_name: Vercel Deploy
category: automation
status: active
source_skill_path: /home/gemmey1020/.codex/skills/vercel-deploy/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Vercel Deploy

## Summary
Deploys applications or websites to Vercel, using preview deployments by default.

## Use When
- Use when a user asks to deploy a project to Vercel.
- Use when a preview deployment link is the intended outcome.

## Do Not Use When
- Do not default to production deployment unless explicitly requested.
- Do not verify the deployed URL by fetching it after deployment.

## Role In Omega Workspace
- Documents the external Vercel deployment workflow available to the workspace.

## Inputs And Preconditions
- Requires a deployable project path or current directory.
- May require Vercel CLI access or the external fallback deploy script.

## Outputs And Effects
- Produces a deployment URL and, in fallback mode, a claim URL.

## Constraints And Non-Goals
- Preview is the default mode.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/vercel-deploy/SKILL.md`
- `/home/gemmey1020/.codex/skills/vercel-deploy/scripts/deploy.sh`

## Notes
- The source skill treats production deploys as explicit-only.
