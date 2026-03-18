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
Generates spoken audio through the OpenAI Audio API using the bundled CLI and built-in voices for narration, voiceover, and accessibility tasks.

## Use When
- Use when text-to-speech or narrated audio output is requested.
- Use when batch speech generation, demo voiceover, IVR prompts, or accessibility reads are needed.

## Do Not Use When
- Do not use for custom voice creation.
- Do not use without the required API key for live calls.
- Do not replace the bundled CLI with ad-hoc one-off scripts.

## Role In Omega Workspace
- Documents the external speech-generation capability as an OpenAI-linked workflow with a CLI-first operating path.

## Inputs And Preconditions
- Requires speech-oriented input text.
- Requires `OPENAI_API_KEY` for live execution in the source skill.
- Assumes the bundled `scripts/text_to_speech.py` workflow is available.

## Outputs And Effects
- Produces speech-oriented audio files through the external CLI workflow.

## Constraints And Non-Goals
- Built-in voices only; custom voice creation is out of scope.
- The source skill defaults to `gpt-4o-mini-tts-2025-12-15` and the `cedar` voice unless the operator chooses otherwise.
- External implementation remains outside this domain.

## Important Source Artifacts
- `/home/gemmey1020/.codex/skills/speech/SKILL.md`
- `/home/gemmey1020/.codex/skills/speech/scripts/text_to_speech.py`

## Notes
- The source skill is tied to the OpenAI Audio API rather than a generic local TTS engine.
- Live usage depends on a local API key and keeps custom-voice workflows out of scope.
- Current official OpenAI docs align with the source skill's use of the `gpt-4o-mini-tts` family and built-in Speech API voices.
