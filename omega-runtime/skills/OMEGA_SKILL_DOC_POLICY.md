# OMEGA SKILL DOCUMENTATION POLICY

## Purpose

`omega-runtime/skills/` is a documentation-only domain.

It exists to document locally installed Codex skills as normalized reference artifacts for this workspace.

## Scope

- This domain is not a source of execution.
- This domain is not a skill runtime.
- This domain does not replace the original local Codex skills.
- The source of truth remains the original skill source under `~/.codex/skills/**/SKILL.md`.

## Required Rules

- Each description must reference the original `source_skill_path`.
- Each description must be operational, not promotional.
- Each description must stay grounded in source evidence.
- Invented capabilities are not allowed.
- Refresh is manual in this phase.

## Forbidden Content

- Copying implementation artifacts is forbidden.
- Do not copy `scripts/`, `assets/`, or `references/`.
- Do not copy full raw `SKILL.md` bodies into this domain.
- Do not add generated execution logic to this domain.

## Update Model

- Source review is manual.
- Description refresh is manual.
- Catalog refresh is manual.
- Any source drift must be resolved by updating the description and catalog entries explicitly.

## Output Standard

- Keep files concise.
- Use English for technical file contents.
- Prefer normalized wording over source duplication.
- Preserve the boundary between documentation and implementation.
