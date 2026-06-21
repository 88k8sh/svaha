# Audit State

last_audit_next: 0
last_audit_date: never
last_audit_tier: none

## Notes
- `last_audit_next`: the _NEXT number that was highest when the last audit ran
- Updated by `/audit` at the end of every run
- Next Tier 1 fires when delta ≥ 5, Tier 2 when delta ≥ 15
