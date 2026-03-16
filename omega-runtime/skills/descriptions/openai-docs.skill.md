---
skill_id: openai-docs
display_name: OpenAI Docs
category: openai
status: active
source_skill_path: /home/gemmey1020/.codex/skills/openai-docs/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# OpenAI Docs

## Summary
Provides current OpenAI guidance using official developer documentation as the source of truth.

## Use When
- Use for OpenAI product or API questions that need current official guidance.
- Use when source attribution or up-to-date model guidance matters.

## Do Not Use When
- Do not use non-official sources first for OpenAI-specific questions.
- Do not rely on memory when official docs can materially change the answer.

## Role In Omega Workspace
- Documents the official-doc lookup path for OpenAI-related work in this workspace.

## Inputs And Preconditions
- Requires an OpenAI-related question or implementation topic.
- Assumes access to the OpenAI docs MCP tools or official-doc fallback flow.

## Outputs And Effects
- Produces concise guidance grounded in official OpenAI documentation.

## Constraints And Non-Goals
- OpenAI docs remain authoritative.
- Reference files are helper context only.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/openai-docs/SKILL.md`

## Notes
- The source skill explicitly prefers MCP doc tools over generic web search.
