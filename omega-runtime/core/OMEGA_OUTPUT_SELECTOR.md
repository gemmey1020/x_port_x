# Ω OUTPUT SELECTOR [V2.0]

Version: 2.0

This document defines how the system chooses the output type after routing is complete.

The Output Selector operates after:

1. Runtime Loader
2. Decision Router

The selector must remain compatible with:

- OMEGA_OUTPUT_CONTRACTS
- OMEGA_MODE_ENGINE
- OMEGA_RESPONSE_SANITIZER

---

# [00] PURPOSE

The selector chooses the smallest valid output type that satisfies:

- mode requirements
- blocking conditions
- mutation policy
- execution contract
- Omega visual output standard

The selector does not generate final formatting.
It selects the output contract that the sanitizer later renders.

---

# [01] ALLOWED OUTPUT TYPES

Allowed output types:

- DIRECT_ANSWER
- CODE_DIFF
- PATCH_BLOCK
- REVIEW_REPORT
- EXECUTION_PLAN
- SIGNAL_ONLY

---

# [02] PRIMARY MODE → OUTPUT MAPPING

ANALYZE

- Output: DIRECT_ANSWER

REVIEW

- Output: REVIEW_REPORT

DIFF

- Output: CODE_DIFF

PATCH

- Output: PATCH_BLOCK

FREEZE

- Output: EXECUTION_PLAN

TRACE

- Output: DIRECT_ANSWER

VOID

- Output: DIRECT_ANSWER

---

# [03] BLOCKING OVERRIDE

If the router returns any blocking signal, the selector must force:

SIGNAL_ONLY

Blocking signals include:

- Ω_IDLE
- Ω_INSUFFICIENT_DATA
- Ω_DENIED_SPECULATION
- Ω_DENIED_SCOPE
- Ω_WAITING_AUTH
- Ω_DENIED_DATA
- Ω_READONLY_MODE
- Ω_CONFLICTING_TRUTH
- Ω_CONFLICTING_INTENT

No other output type is allowed when blocked.

---

# [04] MUTATION-AWARE SELECTION

If mutation is requested and explicitly allowed:

- DIFF → CODE_DIFF
- PATCH → PATCH_BLOCK

If mutation is requested but permission is not explicit:

- force SIGNAL_ONLY
- return Ω_READONLY_MODE

If mutation target is missing:

- force SIGNAL_ONLY
- return Ω_WAITING_AUTH

---

# [05] OUTPUT MINIMIZATION POLICY

The system must choose the smallest valid output that fully satisfies the request.

Priority order:

1. SIGNAL_ONLY
2. CODE_DIFF
3. PATCH_BLOCK
4. REVIEW_REPORT
5. DIRECT_ANSWER
6. EXECUTION_PLAN

This priority must never override correctness.

Example:

- if REVIEW is required, do not downgrade to DIRECT_ANSWER
- if PATCH is required, do not substitute CODE_DIFF unless explicitly requested
- if blocked, always choose SIGNAL_ONLY

---

# [06] VISUAL STANDARD COMPATIBILITY

All non-signal outputs selected here must be renderable through the Omega multiblock visual layout.

Required visual sections for non-signal outputs:

- omega-header
- omega-runtime
- omega-domains
- omega-execution
- omega-result

The selector must assume that rendering discipline is enforced by the sanitizer.

---

# [07] TRACE + VOID RULES

TRACE:

- default output = DIRECT_ANSWER
- must remain bounded
- may summarize runtime state or gate results
- must not expose chain-of-thought

VOID:

- default output = DIRECT_ANSWER
- only valid when authority requirements are satisfied
- must not clear canonical bindings
- must remain compatible with execution contract

---

# [08] SANITIZER COMPATIBILITY

The final output must comply with:

Ω OMEGA OUTPUT — SANITIZER [V2.0]

Selector guarantees:

- exactly one output type
- no mixed output type
- block-compatible routing
- visual-layout-compatible contract selection

---

# [09] FAILURE POLICY

If output type cannot be selected deterministically:

- return SIGNAL_ONLY
- return Ω_DENIED_DATA

If selected output type conflicts with mode engine or execution contract:

- return SIGNAL_ONLY
- return Ω_DENIED_DATA

---

# [OUTPUT_SELECTOR_END]
