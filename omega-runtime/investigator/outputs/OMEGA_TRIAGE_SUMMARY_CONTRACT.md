# OMEGA_Triage_Summary_Contract

## Scope
This is the only output contract allowed in Incident Investigator Foundation Slice 1.
It is a read-only report contract.
It does not authorize remediation, rollback, patching, mutation, or blame language.

## Required Section Order
1. Incident Seed
2. Investigation Status
3. Normalized Identity
4. Source Coverage
5. Top Evidence
6. Correlation Results
7. Contradictions
8. Ranked Hypotheses
9. Confidence
10. Missing Evidence
11. Next Read-Only Steps

## Section Requirements

### 1. Incident Seed
- State the trigger type and trigger value.
- State whether the investigation started from Sentry, logs, or a mixed context.

### 2. Investigation Status
- State one of: `seeded`, `gathering`, `normalized`, `correlated`, `hypothesized`, `blocked`, `reported`.
- If blocked, state the blocking condition explicitly.

### 3. Normalized Identity
- Report the normalized identity fields:
  - `workspace_id`
  - `service_slug`
  - `environment`
  - `release`
  - `request_id`
  - `trace_id`
- Missing values must remain visible as missing or null-equivalent, not silently dropped.

### 4. Source Coverage
- List which sources were actually used.
- Distinguish between available sources and deferred sources.
- GitHub and traces must be marked as out of scope for Slice 1 when relevant.

### 5. Top Evidence
- List the most relevant evidence items with stable evidence references.
- Each item must identify its `source_type` and its `pre_correlation_hint`.

### 6. Correlation Results
- Every correlation entry must cite one class only:
  - `HARD_MATCH`
  - `SOFT_MATCH`
  - `WEAK_HINT`
- Every correlation entry must state the matched keys or the reason it remained weak.

### 7. Contradictions
- Provide a dedicated contradictions section even when the list is empty.
- List contradicting evidence references explicitly.
- State whether each contradiction weakens confidence, blocks correlation, or blocks a stronger claim.

### 8. Ranked Hypotheses
- Provide ranked hypotheses in descending order.
- Every hypothesis must cite supporting evidence references.
- Contradicting evidence must remain visible.
- `likely_root_cause` is an evidence-backed report claim only and must never appear without cited supporting evidence.
- `confirmed_root_cause` is prohibited in Slice 1.

### 9. Confidence
- Use one label only:
  - `LOW`
  - `MEDIUM`
  - `HIGH`
- Confidence must include a short rationale tied to evidence quality, not tone.

### 10. Missing Evidence
- State what key evidence is missing.
- State whether the gap blocks correlation, weakens confidence, or blocks a stronger claim.
- Missing evidence must be explicit even when a leading hypothesis exists.

### 11. Next Read-Only Steps
- Suggest only read-only next steps.
- Allowed examples:
  - gather more logs
  - inspect more Sentry events
  - inspect release context
  - request missing identifiers
  - defer external sources

## Prohibited Claims
- `confirmed root cause`
- remediation guidance
- rollback guidance
- patch suggestions
- blame language
- hidden uncertainty
- unsupported business impact statements

## Output Discipline
- The report must stay evidence-first.
- Unsupported conclusions must degrade to uncertainty or blocked status.
- The contract defines the payload only; it does not replace existing runtime output wrappers.
