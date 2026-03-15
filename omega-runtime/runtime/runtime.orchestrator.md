# RUNTIME ORCHESTRATOR

The orchestrator must:

1. Read all stateful files before decision
2. Never generate output before DecisionRecord exists
3. Route blocked requests to signal-only path
4. Route allowed requests to bounded generation path
5. Pass every generated response through sanitizer
6. Append every decision to audit trail
