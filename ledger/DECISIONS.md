# DECISIONS — Design Decisions + Alternatives Considered

Append-only. One block per non-trivial design decision: what was chosen, what was rejected, and why.
The "road not taken" log — so a future session doesn't reopen a settled question or repeat a discarded approach.

---

## Format

```
## YYYY-MM-DD — [decision in one line]
- **Chose:** [what was decided]
- **Over:** [the alternative(s) rejected]
- **Why:** [the reasoning that decided it]
```

---

## 2026-06-24 — double-booking guard: soft occupancy hint over a hard lock
- **Chose:** an advisory `_NEXT_NNN.booted` sidecar (`bin/next-boot.sh`) that `next-live.sh` surfaces as `⚠ in use` / `· booted HH:MM` and the no-arg pickers skip (the tiebreak) — a soft hint, cleared on retire.
- **Over:** (a) a hard lock that refuses to boot a held slot; (b) doing nothing.
- **Why:** the `_NEXT` plumbing is already collision-safe (idempotent consume + atomic mint), but two sessions on one slot still race on shared output files — so "nothing" was insufficient. A hard lock costs a stale-lock reaper (boot is read-only, so crashes/reflection-closes leak the lock), and the only workable reaper is a TTL, which just re-creates the "is it really still live?" judgment the system already leaves to a human. Its marginal benefit over the hint (block vs. warn) is small against that permanent cost. The advisory hint needs no reaper — nothing depends on its accuracy, so a stale one is harmless. Residual (accepted): truly sub-second simultaneous boots can still miss each other's hint; the soft guard narrows the window, not closes it.
