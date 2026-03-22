---
skill_id: omega-ai-runtime
display_name: Omega AI Runtime
category: openai
status: active
source_skill_path: /home/gemmey1020/.codex/skills/omega-ai-runtime/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Omega AI Runtime

## Summary
Builds decision-complete runtime specifications for AI features, including OpenAI surface choice, model selection, prompt contracts, tools, evals, and operations.

## Use When
- Use when the main uncertainty is the AI runtime architecture rather than ordinary implementation.
- Use when an AI feature needs a concrete contract for models, tools, schemas, prompts, and validation.

## Do Not Use When
- Do not use for repo mapping, ordinary coding work, or post-implementation proof selection.
- Do not use as a generic prompt-writing shortcut without runtime design intent.

## Role In Omega Workspace
- Documents the external AI-runtime design skill that turns vague AI feature ideas into implementable contracts for this workspace.

## Inputs And Preconditions
- Requires an AI feature or integration question with unresolved runtime, model, tool, or eval decisions.
- Assumes OpenAI-specific choices will be checked against current official documentation before finalizing recommendations.

## Outputs And Effects
- Produces runtime specs covering chosen API surface, model strategy, prompt/tool contracts, eval plans, and operational notes.

## Constraints And Non-Goals
- Design-focused only; it does not implement the runtime itself.
- Keeps current OpenAI documentation authoritative over stale local memory or helper references.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/omega-ai-runtime/SKILL.md`
- `/home/gemmey1020/.codex/skills/omega-ai-runtime/scripts/runtime_spec_template.py`

## Notes
- The source skill explicitly treats runtime choice and model choice as related but separate decisions.
