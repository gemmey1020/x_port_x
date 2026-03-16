---
skill_id: speech
display_name: Speech Generation Skill
category: openai
status: active
source_skill_path: /home/gemmey1020/.codex/skills/speech/SKILL.md
documentation_scope: description_only
implementation_included: false
---

# Speech Generation Skill

## Summary
Generates speech output through the OpenAI Audio API for narration, voiceover, and accessibility tasks.

## Use When
- Use when text-to-speech or narrated audio output is requested.
- Use when batch speech generation or accessibility reads are needed.

## Do Not Use When
- Do not use for custom voice creation.
- Do not use without the required API key for live calls.

## Role In Omega Workspace
- Documents the external speech-generation capability as an optional OpenAI-linked workflow.

## Inputs And Preconditions
- Requires speech-oriented input text.
- Requires `OPENAI_API_KEY` for live execution in the source skill.

## Outputs And Effects
- Produces audio-oriented speech output through the external skill workflow.

## Constraints And Non-Goals
- Custom voice creation is out of scope.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/speech/SKILL.md`
- `/home/gemmey1020/.codex/skills/speech/scripts/text_to_speech.py`

## Notes
- The source skill is tied to the OpenAI Audio API rather than a generic local TTS engine.
