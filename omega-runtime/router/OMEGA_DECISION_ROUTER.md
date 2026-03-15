# OMEGA_DECISION_ROUTER

Decision flow:

1. Parse intent
2. Resolve authority
3. Run input gates
4. Check constraints
5. Check artifact registry
6. Check continuity binding
7. Select mode
8. Select output type
9. Assign truth basis
10. Emit DecisionRecord

DecisionRecord fields:

- allowed
- signal
- mode
- output_type
- truth_basis
- authority_used
- changes_allowed
- blocking_reason
