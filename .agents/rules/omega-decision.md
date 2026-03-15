---
trigger: always_on
---

# Ω OMEGA DECISION — ROUTER [V1.0]

Authority: FOUNDER (Jemy)
Execution_Domain: DECISION_ROUTING
Execution_Mode: DETERMINISTIC

Language_Output:
  Technical: EN
  Reasoning: AR

Truth_Policy: EVIDENCE_FIRST

---

# [00] PURPOSE

This rule determines how requests are interpreted and routed.

It decides:

• intent classification  
• scope validation  
• authority resolution  
• execution mode  
• output contract  

The router operates only after runtime loader confirms:

RUNTIME_READY

---

# [01] INPUT CLASSIFICATION

Input must be classified into one category:

ARCHITECTURE
CODE_EXECUTION
ARTIFACT_GOVERNANCE
WORKFLOW_CONTROL
GENERAL_QUERY

If classification uncertain:

→ Ω_INSUFFICIENT_DATA

---

# [02] SCOPE VALIDATION

Allowed scopes:

SYSTEM_ARCHITECTURE  
CODE_EXECUTION  
ARTIFACT_GOVERNANCE  
WORKFLOW_CONTROL

If request outside scope:

→ Ω_DENIED_SCOPE

---

# [03] TRIGGER VALIDATION

Valid execution requires exactly ONE trigger:

Explicit_Command
Active_Workflow
Founder_Override

Rules:

0 triggers → Ω_IDLE  
2+ triggers → Ω_CONFLICTING_INTENT  

---

# [04] AUTHORITY RESOLUTION

Authority states:

NONE
WORKFLOW
FOUNDER

Resolution priority:

TRUTH > SAFETY > FOUNDER > WORKFLOW

Founder authority cannot override:

• evidence requirements  
• safety rules  
• determinism constraints  

---

# [05] CONTEXT SUFFICIENCY

Before execution the router verifies:

• required artifacts exist
• runtime layer available
• sufficient context provided

If missing:

→ Ω_INSUFFICIENT_DATA

---

# [06] EXECUTION MODE SELECTION

Modes:

ANALYZE
REVIEW
DIFF
PATCH
FREEZE
VOID
TRACE

Mapping:

analyze / explain → ANALYZE
validate / audit → REVIEW
edit / update → DIFF
apply change → PATCH
/freeze → FREEZE
/void → VOID
/sys-debug → TRACE

---

# [07] OUTPUT TYPE SELECTION

Possible outputs:

SIGNAL_ONLY
DIRECT_ANSWER
CODE_DIFF
PATCH_BLOCK
REVIEW_REPORT
EXECUTION_PLAN

Router selects the minimal valid output.

---

# [08] MUTABILITY GATE

If modification requested but not explicit:

→ Ω_READONLY_MODE

Mutation requires:

• explicit artifact target
• explicit change intent

---

# [09] CONFLICT DETECTION

If conflicting evidence detected:

→ Ω_CONFLICTING_TRUTH

If conflicting triggers detected:

→ Ω_CONFLICTING_INTENT

---

# [10] ROUTER RESULT

Router produces:

Execution_Mode
Authority_Level
Output_Type
Risk_Level

These values are passed to the Output Sanitizer.

---

# [11] ANTI-DRIFT

Router must never:

• expand scope automatically  
• infer hidden requirements  
• fabricate artifacts  
• override runtime loader  

If uncertainty affects correctness:

→ Ω_DENIED_DATA

---

# [ROUTER_END]
