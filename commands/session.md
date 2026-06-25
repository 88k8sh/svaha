# /session — Smart session boot

Three modes:

- `/session` (no arg) — auto-pick the lowest-numbered `_NEXT` with pending moves
- `/session list` — show all open sessions with a summary of each
- `/session N` — boot from `_NEXT_NNN.md` directly (e.g. `/session 41` → `_NEXT_041.md`)

**Alias:** saying **"svaha"** as the opening word of a session is an alias for `/session list` (show the live set, then pick) — see `CLAUDE.md` "## Boot". It's the opening counterpart to the स्वाहा handoff seal; a svaha-boot shows the list and leads the eventual boot with the status block, never echoing the seal back.

**Resolve `<system-dir>` first** (per CLAUDE.md's "Two paths" rule): the dir holding a `_LOADUP.md`, found by a bounded search around CWD — the nearest dir at/above CWD, else the single immediate child of CWD that has one (the nested-workspace case). CWD + ancestors + one level of children, never recursive. `<kit-dir>` is already absolute wherever it appears. Nothing found → the project isn't initialized; run `/init`.

---

## `/session list`

**Do NOT eyeball the folder.** `<system-dir>/next/` is shared mutable state — concurrent sessions consume `_NEXT` files in real time, so any hand-built list is a racy snapshot that silently drops a just-retired session (a parallel `/handoff` can consume a `_NEXT` mid-conversation; an eyeballed list drops it with no signal). Always run the canonical source-of-truth script:

```
<kit-dir>/bin/next-live.sh <system-dir>
```

It prints the deterministic live set **and** any sessions consumed in the last 120 min (so a session retired by a concurrent handoff is shown explicitly, never vanishes) **and** any desyncs (`DONE-UNCONSUMED` = move finished but never stamped; `ORPHAN` = stray `.consumed`). Relay its output verbatim, then append the boot pointer:

```
→ svaha to boot lowest, or /session N for a specific one
```

If `recently consumed` is non-empty, say so in one line — don't let a just-retired session disappear unmentioned. A live slot may also carry an occupancy hint — `⚠ in use (booted HH:MM …)` (booted in the last few minutes, likely a concurrent session right now) or `· booted HH:MM (may be in use)` — relay these verbatim; they help the pick avoid a slot another session is on (advisory only, never a lock). Stop here — do not boot. (A follow-up **svaha** is position-2 assent — it boots the lowest live session without needing `/session`.)

---

## `/session` (no arg) and `/session N`

**Step 1 — resolve the target file:**
- No arg: run `<kit-dir>/bin/next-live.sh <system-dir>` (the canonical live-set script — do not eyeball the folder) and pick the **lowest-numbered** entry in its `live sessions` list **that is NOT marked `⚠ in use`** (the occupancy tiebreak — that slot was booted in the last few minutes, most likely by a concurrent session, so skip it to avoid double-booking). If *every* live entry is `⚠ in use`, pick the lowest anyway and say so in one line (occupancy is advisory, not a lock). If the live list is empty, say so and stop.
- Arg is `list`: run `/session list` mode above.
- Arg is a number N: zero-pad to 3 digits → `<system-dir>/next/_NEXT_NNN.md`. If missing, flag and stop.

**Step 1b — stamp occupancy (boot only, not `list`):** once the target slot is resolved (no-arg or N), mark it in-use so a concurrent session's `/session list` and no-arg pick can see you're on it:

```
<kit-dir>/bin/next-boot.sh <system-dir> NNN
```

This writes/refreshes the advisory `_NEXT_NNN.booted` sidecar (cleared automatically when the slot is consumed at handoff). It is a soft hint, never a lock — it blocks nothing, so just run it and proceed.

**Step 2 — git pull (if repo):** `git -C <system-dir> rev-parse --git-dir 2>/dev/null`. If repo, run `git -C <system-dir> pull` before reading files.

**Step 3 — read files:**
- The resolved `_NEXT_NNN.md`
- `<system-dir>/_LOADUP.md`
- `<system-dir>/ledger/USER_TASKS.md` (for task count only)

**Step 4 — on-demand pre-load:** scan `## Next moves` for any `(requires: X)` annotations. If present, load those files now before emitting the status block — not mid-task.

**Step 4b — RESUME-WITH-VERIFICATION (before the status block):** a handoff is a claim, not a fact — verify it before acting on it. Run the cheap checks (just `git` + `grep`, no DB, no agents) exactly as specified in `boot.md`'s **RESUME-WITH-VERIFICATION** section — the single source of truth for this logic:
- **Step A** — read the `checkpoint:` field; if it's a resolvable SHA in a git repo, run `git -C <system-dir> diff --stat <checkpoint>..HEAD` for the ground truth of what changed since the handoff was written; if `n/a` / unresolvable, fall back to grep-only.
- **Step B** — registry-first, then the reads-grep: for each open move, first `grep` `<system-dir>/ledger/EXTERNAL_DELIVERABLES.md` for an out-of-tree supersession (catches completions no in-tree gate can see), then inspect the files/sections its `reads:` hint names (cross-check `skip:`), classifying it `still-true` / `already-done` / `stale` / `superseded` / `unverified`. (`boot.md`'s Step B is canonical for how — do not restate it here.)
- **Step C** — report one `claimed: … / verified: …` line per move in the status block, then gate Step 6: only `still-true` moves auto-execute.
- **Step D** — same-file-clobber check: cross-check move 1's intended edits against the `touched:` lists of other still-live slots (`next-live.sh` for the live set, `grep -h '^touched:' <system-dir>/next/_NEXT_*.md` for their edit-lists); warn on an overlap, then proceed (advisory, not a block).

This is the structural fix for silent-dropout and booted-into-consumed-work. **`boot.md` is canonical for the A/B/C/D procedure — do not restate it here, so the two can't drift.**

**Step 5 — emit status block (no opener/file mismatch check — no opener exists):**

```
loaded: _NEXT_NNN ✓  _LOADUP ✓  [any requires: files] ✓
phase: [current work mode]
tasks: N open
verified: <checkpoint SHA or n/a> — one claimed/verified line per open move
  claimed: <move text>  /  verified: still-true | already-done | stale | superseded | unverified
next: [system] move 1 — <move text> (<model> / <effort>)
```

**Step 6 — auto-continue (gated by Step 4b):** execute the first move that verified **still-true** immediately. Do not ask "shall I start?" — the open moves are the direction. **But do not blindly execute a move that verified `already-done`, `stale`, or `superseded`** — flag it instead, say why, and move to the next live move (or report the queue is exhausted). An `unverified` move may run, but say so first. This gate is what stops the loop from re-doing consumed work.

---

## On-demand rules

Same as `/boot` — pull only when the session task explicitly needs them. Do NOT load on-demand files unless a move or task requires it.
