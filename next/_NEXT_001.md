# _NEXT_001 — initial seed

outcome: SUCCEEDED    ← enum: SUCCEEDED | PARTIAL_PLUS | PARTIAL_MINUS | FAILED (UNKNOWN optional)
touched: none    ← files this session edited; the next boot's same-file-clobber check reads this
checkpoint: n/a    ← seed file; no handoff SHA. Real handoffs get the short-SHA stamped by next-write.sh.

worked: seeding the handoff loop with a verifiable example move
failed: none — initial seed

## Pending
none — initial seed file

## Next moves
1. [system] Run boot and confirm the status block + verified: lines output correctly — Sonnet / low
   reads: boot.md (RESUME-WITH-VERIFICATION section), _LOADUP.md §7 (boot status format)
   skip: nothing yet — this is the first boot
2. [system] Run /handoff at end of first real session to write _NEXT_002.md (with outcome/checkpoint stamped) — Sonnet / low
   reads: handoff.md (step 2 write template), bin/next-write.sh (checkpoint stamping)

## Push to _LOADUP
none
