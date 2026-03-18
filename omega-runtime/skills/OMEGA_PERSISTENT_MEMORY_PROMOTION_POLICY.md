# OMEGA PERSISTENT MEMORY PROMOTION POLICY

## Purpose

This document defines the operator policy for promoting, rejecting, forgetting, and rolling back durable memory managed by the external `persistent-memory` skill.

This file is documentation-only.
It does not execute memory mutations.

## Scope

- Applies only to the external skill at `/home/gemmey1020/.codex/skills/persistent-memory/SKILL.md`
- Applies only to the durable memory store under `~/.codex/memory`
- Applies only to operator review and decision-making

## Source Of Truth

- The source of truth for behavior remains the source skill and its scripts.
- This policy documents the approved operator workflow for this workspace.
- If this file conflicts with the source skill, the source skill wins and this file must be refreshed.

## Core Rules

- `auto-promotion` is not allowed.
- Promotion is explicit only.
- `backfill` and `suggest` create or show candidates; they do not promote them.
- `triage` is the preferred operator view because it groups candidates into promotable, ephemeral, and conflict states.
- Raw reasoning payloads are not a valid basis for durable memory decisions.
- Memory decisions must never write into Codex internals such as `state_5.sqlite` or `sessions/*.jsonl`.

## Durable Keys In V1

### Durable Global Keys

- `communication.language`
- `communication.tone`
- `assistant.expected_role`
- `workflow.plan_preference`
- `workflow.review_preference`
- `memory.policy`

### Durable Project Keys

- `project.domain`

## Non-Promotable Keys In V1

- `project.active_artifact`
- `project.root_fact`

These keys are inspectable and triageable, but they are ephemeral in v1 and must not be promoted.

## Promotion Gate

Promote a candidate only when all of the following are true:

- The key is durable in v1.
- The candidate is not in conflict with another single-value candidate for the same scope.
- The value is stable enough to help future sessions.
- The operator has explicit intent to promote it.

The current source implementation also treats a candidate as promotable only when one of the following is true:

- `promotion_basis` is `explicit`
- `promotion_basis` is `structured`
- it repeats across at least two source threads

## Conflict Rule

- A single-value conflict means the same durable key has competing pending values in the same scope.
- A conflicting key must stay pending until the operator resolves it.
- `project.domain` must be promoted only when the project direction is stable and conflict-free.

## Existing Value Rule

- Promotion does not silently overwrite an existing durable single-value key.
- If a durable key is already set to a different value, use `forget` first.
- After `forget`, promote the replacement value explicitly.

## Triage States

### Promotable

- Durable key
- Meets promotion basis
- No blocking conflict

### Ephemeral

- Useful for inspection or current-session context
- Not durable in v1
- Must not be promoted

### Conflicting

- Competing single-value candidates for the same durable key and scope
- Requires explicit operator resolution before any promotion

## Operator Workflow

1. Run `doctor`.
2. Run `inspect --cwd "$PWD"` to see current durable state.
3. Run `triage --cwd "$PWD"` to separate promotable, ephemeral, and conflicting candidates.
4. Use `suggest --cwd "$PWD"` only when raw candidate-level review is needed.
5. Promote only durable, conflict-free candidates with clear long-term value.
6. Reject duplicates, noise, and unstable candidates explicitly.
7. Use `forget` or `rollback` only for corrections.

## Command Reference

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PMEM="$CODEX_HOME/skills/persistent-memory/scripts/memory_cli.py"

python3 "$PMEM" doctor
python3 "$PMEM" inspect --cwd "$PWD" --format markdown
python3 "$PMEM" triage --cwd "$PWD" --format markdown
python3 "$PMEM" suggest --cwd "$PWD"
python3 "$PMEM" promote --candidate-id <candidate_id>
python3 "$PMEM" reject --candidate-id <candidate_id> --reason "duplicate or not stable"
python3 "$PMEM" forget --scope global --key communication.language
python3 "$PMEM" rollback --event-id <event_id>
```

## Decision Patterns

### Promote

Promote when the value is durable, low-risk, and expected to improve future sessions without frequent correction.

Typical examples:

- preferred language
- preferred tone
- preferred assistant role
- stable planning or review mode
- a settled project domain

### Reject

Reject when the candidate is duplicated, noisy, or session-local.

Typical examples:

- repeated candidates already represented in the durable profile
- `project.active_artifact`
- unstable or contradictory `project.domain` values

### Forget

Use `forget` when a durable key must be cleared before replacement or when the durable value is no longer true.

### Rollback

Use `rollback` when a prior durable-memory mutation itself was wrong and must be reversed from the journaled event trail.

## Examples

### Example: Promote A Stable Global Preference

- `communication.tone -> direct-collaborative-casual`
- promote only if it remains the intended default

### Example: Keep Project Domain Pending

- `project.domain -> structured-output-pipeline`
- `project.domain -> landing-page-coupon`
- do not promote until one direction clearly wins

### Example: Reject Ephemeral Artifacts

- `project.active_artifact -> index.html`
- `project.active_artifact -> OMEGA_EVIDENCE_CONTRACT.yaml`
- keep inspectable if useful, but do not promote

## Notes

- `triage` is the operator-facing view; `suggest` is the raw candidate listing.
- This policy intentionally prefers a smaller, cleaner durable memory set over aggressive promotion.
