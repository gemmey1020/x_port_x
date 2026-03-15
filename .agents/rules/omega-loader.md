---
trigger: always_on
---

# Ω OMEGA RUNTIME — LOADER [V1.0]

Authority: FOUNDER (Jemy)
Execution_Domain: RUNTIME_LOADING
Drift_Tolerance: 0.0
Execution_Mode: DETERMINISTIC

Language_Output:
  Technical: EN
  Reasoning: AR

Truth_Policy: FILE_FIRST
Memory_Policy: DISABLED_FOR_RUNTIME

---

# [00] PURPOSE

This rule governs how the Omega runtime is loaded.

It guarantees that operational behavior is driven by workspace runtime artifacts rather than model assumptions.

This rule is responsible for:

• runtime discovery  
• runtime dependency validation  
• runtime loading order  
• runtime integrity checks  

The runtime loader must execute before routing or execution decisions.

---

# [01] REQUIRED RUNTIME ROOT

The runtime root must exist in the workspace:

omega-runtime/

If this directory is missing:

→ RETURN SIGNAL: Ω_WAITING_AUTH

---

# [02] REQUIRED RUNTIME STRUCTURE

The loader expects the following structure:

omega-runtime/
│
├── core/
│
├── state/
│
├── router/
│
├── filters/
│
├── audit/

If any required domain is missing:

→ Ω_WAITING_AUTH

---

# [03] LOADING ORDER

Runtime components must be resolved in the following deterministic order:

1️⃣ core  
2️⃣ state  
3️⃣ router  
4️⃣ filters  
5️⃣ audit  

Each domain may depend only on earlier domains.

Forbidden:

• circular dependencies  
• late dependency injection  
• runtime mutation during loading

---

# [04] CORE DOMAIN

`core/` contains immutable operational contracts.

Examples:

core/contracts.json
core/modes.json
core/signals.json
core/authority_map.json

Rules:

• core artifacts are READ_ONLY  
• core artifacts cannot mutate during session  

If corrupted:

→ Ω_DENIED_DATA

---

# [05] STATE DOMAIN

`state/` contains runtime state snapshots.

Examples:

state/workflow.json
state/context_lock.json
state/runtime_budget.json

Rules:

• state may update during execution
• updates must remain deterministic
• updates cannot mutate core contracts

---

# [06] ROUTER DOMAIN

`router/` contains execution routing maps.

Examples:

router/intent_map.json
router/mode_map.json
router/authority_map.json

These files assist the Decision Router rule.

They must be loaded but not interpreted by the Loader.

---

# [07] FILTERS DOMAIN

`filters/` contains behavioral restrictions.

Examples:

filters/scope_rules.json
filters/security_rules.json
filters/drift_rules.json

Filters may block routing but cannot override constitutional axioms.

---

# [08] AUDIT DOMAIN

`audit/` contains runtime logs or verification data.

Examples:

audit/execution_log.json
audit/runtime_hash.json

Audit files are READ_ONLY during analysis unless explicitly requested.

---

# [09] RUNTIME INTEGRITY RULES

Loader must validate:

• file readability  
• deterministic ordering  
• absence of circular references  

If runtime integrity cannot be guaranteed:

→ Ω_DENIED_DATA

---

# [10] FAILURE CONDITIONS

The loader must halt execution if:

• runtime root missing
• required domain missing
• corrupted core contracts
• dependency loop detected

Signals:

Ω_WAITING_AUTH  
Ω_DENIED_DATA

---

# [11] LOADER OUTPUT

The loader does not execute tasks.

It produces one of the following internal states:

RUNTIME_READY
RUNTIME_BLOCKED
RUNTIME_CORRUPTED

Routing and execution must not begin unless:

RUNTIME_READY

---

# [12] ANTI-DRIFT

The loader must never:

• fabricate runtime files  
• infer missing runtime artifacts  
• replace runtime artifacts with model assumptions  

If runtime missing:

→ Ω_WAITING_AUTH

---

# [LOADER_END]
