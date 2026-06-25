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

## 2026-06-25 — boot-sweep-guard hook NOT mirrored into the kit (registry shipped, guard deferred)
- **Chose:** ship the out-of-tree registry (`bin/external-done.sh` + `ledger/EXTERNAL_DELIVERABLES.md`) and the registry-first `boot.md` Step B (v0.6.0), but do NOT add a boot-sweep-guard Stop hook.
- **Over:** porting the in-tree `boot-sweep-guard.sh` (keys on a mandatory `EXTERNAL_DELIVERABLES` grep tool_use); and a kit-native `resume-verify-guard` (keys on the `claimed:…/verified:…` status-block line).
- **Why:** the in-tree guard is skip-proof only because in-tree Step 4b is a HARD GATE that mandates the registry grep on every boot. The kit's Step B registry probe is CONDITIONAL — on a fresh install (seed has only illustrative rows, no real out-of-tree shadow) the grep yields nothing actionable, so no reliably-present tool_use exists for a hook to key on; a ported guard would false-fire on ordinary boots. Cost is high and permanent (always-on Stop hook + settings.json.snippet entry + MANIFEST/SYNC_MAP/Layer-3 couplings + doctor hook-count bump 6→7); benefit is low (the kit already covers the booted-into-consumed-work class three ways: Step B classify-and-gate, `next-live.sh` DONE-PROBABLE, `handoff.md` Supersede stamp). High cost + low marginal benefit → take the lighter path. **Revisit if:** the kit grows a HARD-GATE mandatory-grep Step (matching in-tree's structure) OR the user asks for it — then port a `resume-verify-guard` keying on BOOT=`loaded:.*_NEXT_[0-9]` + VERIFIED=`claimed:.*verified:` (the only kit-native skip-proof anchor), NOT the in-tree EXTERNAL_DELIVERABLES grep, registered in Stop group 1 as `bash $HOME/.claude/hooks/…`.

## 2026-06-24 — double-booking guard: soft occupancy hint over a hard lock
- **Chose:** an advisory `_NEXT_NNN.booted` sidecar (`bin/next-boot.sh`) that `next-live.sh` surfaces as `⚠ in use` / `· booted HH:MM` and the no-arg pickers skip (the tiebreak) — a soft hint, cleared on retire.
- **Over:** (a) a hard lock that refuses to boot a held slot; (b) doing nothing.
- **Why:** the `_NEXT` plumbing is already collision-safe (idempotent consume + atomic mint), but two sessions on one slot still race on shared output files — so "nothing" was insufficient. A hard lock costs a stale-lock reaper (boot is read-only, so crashes/reflection-closes leak the lock), and the only workable reaper is a TTL, which just re-creates the "is it really still live?" judgment the system already leaves to a human. Its marginal benefit over the hint (block vs. warn) is small against that permanent cost. The advisory hint needs no reaper — nothing depends on its accuracy, so a stale one is harmless. Residual (accepted): truly sub-second simultaneous boots can still miss each other's hint; the soft guard narrows the window, not closes it.
