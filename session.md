# /session — Smart session boot

Three modes:

- `/session` (no arg) — auto-pick the lowest-numbered `_NEXT` with pending moves
- `/session list` — show all open sessions with a summary of each
- `/session N` — boot from `_NEXT_NNN.md` directly (e.g. `/session 41` → `_NEXT_041.md`)

---

## `/session list`

**Do NOT eyeball the folder.** `<system-dir>/next/` is shared mutable state — concurrent sessions consume `_NEXT` files in real time, so any hand-built list is a racy snapshot that silently drops a just-retired session (a parallel `/handoff` can consume a `_NEXT` mid-conversation; an eyeballed list drops it with no signal). Always run the canonical source-of-truth script:

```
<system-dir>/bin/next-live.sh <system-dir>
```

It prints the deterministic live set **and** any sessions consumed in the last 120 min (so a session retired by a concurrent handoff is shown explicitly, never vanishes) **and** any desyncs (`DONE-UNCONSUMED` = move finished but never stamped; `ORPHAN` = stray `.consumed`). Relay its output verbatim, then append the boot pointer:

```
→ /session to auto-boot lowest, or /session N for a specific one
```

If `recently consumed` is non-empty, say so in one line — don't let a just-retired session disappear unmentioned. Stop here — do not boot.

---

## `/session` (no arg) and `/session N`

**Step 1 — resolve the target file:**
- No arg: run `<system-dir>/bin/next-live.sh <system-dir>` (the canonical live-set script — do not eyeball the folder) and pick the **lowest-numbered** entry in its `live sessions` list. If that list is empty, say so and stop.
- Arg is `list`: run `/session list` mode above.
- Arg is a number N: zero-pad to 3 digits → `<system-dir>/next/_NEXT_NNN.md`. If missing, flag and stop.

**Step 2 — git pull (if repo):** `git -C <system-dir> rev-parse --git-dir 2>/dev/null`. If repo, run `git -C <system-dir> pull` before reading files.

**Step 3 — read files:**
- The resolved `_NEXT_NNN.md`
- `<system-dir>/_LOADUP.md`
- `<system-dir>/30_LEDGER/USER_TASKS.md` (for task count only)

**Step 4 — on-demand pre-load:** scan `## Next moves` for any `(requires: X)` annotations. If present, load those files now before emitting the status block — not mid-task.

**Step 4b — RESUME-WITH-VERIFICATION (before the status block):** a handoff is a claim, not a fact — verify it before acting on it. Run the cheap checks (just `git` + `grep`, no DB, no agents) exactly as specified in `boot.md`'s **RESUME-WITH-VERIFICATION** section — the single source of truth for this logic:
- **Step A** — read the `checkpoint:` field; if it's a resolvable SHA in a git repo, run `git -C <system-dir> diff --stat <checkpoint>..HEAD` for the ground truth of what changed since the handoff was written; if `n/a` / unresolvable, fall back to grep-only.
- **Step B** — for each open move, inspect the files/sections its `reads:` hint names (and cross-check the `skip:` list), classifying it `still-true` / `already-done` / `stale` / `unverified`.
- **Step C** — report one `claimed: … / verified: …` line per move in the status block, then gate Step 6: only `still-true` moves auto-execute.
- **Step D** — same-file-clobber check: cross-check move 1's intended edits against the `touched:` lists of other still-live slots (`next-live.sh` for the live set, `grep -h '^touched:' <system-dir>/next/_NEXT_*.md` for their edit-lists); warn on an overlap, then proceed (advisory, not a block).

This is the structural fix for silent-dropout and booted-into-consumed-work. **`boot.md` is canonical for the A/B/C/D procedure — do not restate it here, so the two can't drift.**

**Step 5 — emit status block (no opener/file mismatch check — no opener exists):**

```
loaded: _NEXT_NNN ✓  _LOADUP ✓  [any requires: files] ✓
phase: [current work mode]
tasks: N open
verified: <checkpoint SHA or n/a> — one claimed/verified line per open move
  claimed: <move text>  /  verified: still-true | already-done | stale | unverified
next: [system] move 1 — <move text> (<model> / <effort>)
```

**Step 6 — auto-continue (gated by Step 4b):** execute the first move that verified **still-true** immediately. Do not ask "shall I start?" — the open moves are the direction. **But do not blindly execute a move that verified `already-done` or `stale`** — flag it instead, say why, and move to the next live move (or report the queue is exhausted). An `unverified` move may run, but say so first. This gate is what stops the loop from re-doing consumed work.

---

## On-demand rules

Same as `/boot` — pull only when the session task explicitly needs them. Do NOT load on-demand files unless a move or task requires it.
