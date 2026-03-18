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
Provides current OpenAI guidance through official developer documentation, using the OpenAI docs MCP workflow as the primary lookup path.

## Use When
- Use for OpenAI product or API questions that need current official guidance.
- Use when source attribution, model selection, or GPT-5.4 upgrade guidance matters.

## Do Not Use When
- Do not use generic web search before the docs MCP tools for OpenAI-specific work.
- Do not rely on memory or helper references when official docs can materially change the answer.

## Role In Omega Workspace
- Documents the official-doc lookup path for OpenAI-related work in this workspace, including MCP-first retrieval and official-domain fallback.

## Inputs And Preconditions
- Requires an OpenAI-related question or implementation topic.
- Assumes access to the OpenAI docs MCP tools or the source skill's official-doc fallback flow.

## Outputs And Effects
- Produces concise, cited guidance grounded in official OpenAI documentation.

## Constraints And Non-Goals
- OpenAI docs remain authoritative.
- Reference files are helper context only.
- Fallback browsing stays restricted to official OpenAI domains.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/openai-docs/SKILL.md`
- `/home/gemmey1020/.codex/skills/openai-docs/references/latest-model.md`
- `/home/gemmey1020/.codex/skills/openai-docs/references/upgrading-to-gpt-5p4.md`

## Notes
- The source skill explicitly prefers MCP `search` and `fetch` flows before any web fallback.
- Arabic answers from the source skill are expected to carry a `Sources` section with official links.
