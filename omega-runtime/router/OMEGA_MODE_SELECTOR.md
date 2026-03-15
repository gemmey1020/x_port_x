# OMEGA_MODE_SELECTOR

Selection precedence:

1. Explicit trigger
2. Output type lock
3. Parsed intent
4. Workflow state
5. Default safe mode

Examples:

- "Explain this architecture" -> ANALYZE
- "Review this plan" -> REVIEW
- "Patch this file" -> PATCH
- "/freeze" -> FREEZE
