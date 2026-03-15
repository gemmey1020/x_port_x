# OMEGA_INTENT_PARSER

Intent classes:

- THINK_ALOUD
- DIRECT_QUESTION
- REVIEW_ORDER
- PATCH_ORDER
- DIFF_ORDER
- FREEZE_ORDER
- VOID_ORDER
- CONTINUITY_REBIND
- SCOPE_EXPANSION_REQUEST

Parsing rules:

1. If user asks to explain/analyze/audit -> ANALYZE or REVIEW
2. If user asks to modify specific artifact -> DIFF or PATCH
3. If user provides trigger /freeze -> FREEZE
4. If user references prior work without artifact/pointer -> continuity = unbound
5. If request is statement only -> THINK_ALOUD
