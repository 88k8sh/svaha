# /boot — Session Boot Sequence

Execute immediately, no preamble. Two files — always.

## Pre-read (before loading anything)

**Resolve `<system-dir>` first** (per CLAUDE.md's "Two paths" rule): the dir holding a `_LOADUP.md`, found by a bounded search around CWD — the nearest dir at/above CWD, else the single immediate child of CWD that has one (the nested-workspace case). CWD + ancestors + one level of children, never recursive. `<kit-dir>` is already absolute wherever it appears. If nothing is found, the project isn't initialized — run `/init`.

**Git pull (if repo):** check `git -C <system-dir> rev-parse --git-dir 2>/dev/null`. If <system-dir> is a git repo, run `git -C <system-dir> pull` before reading any files. Stale files silently misdirect sessions.

## Always load (every session)

1. **Prefer `/session N`** for normal boots — it reads the `_NEXT` directly without a paste block. Use `boot` only when explicitly invoked with a pasted opener block containing a `resume:` line. If a paste block was provided: read the `_NEXT_NNN.md` named in its `resume:` line. If no paste block: apply `/session` auto-pick logic — scan `<system-dir>/next/`, find the lowest-numbered `_NEXT_NNN.md` with open moves, and flag which file you're using. These are parallel session slots, so a higher number is another session's handoff, not a newer version of yours. If the named file is missing, flag it. Read it for pending work, settled facts, open moves.

   **Opener/file mismatch guard (hard check).** After reading the named `_NEXT`, compare its `## Next moves` against the bullet moves in the opener block. If they **do not match** (the opener lists moves absent from the file, or the file's moves are already done), do NOT silently proceed — the opener was produced by a malformed handoff that recycled a consumed `_NEXT` instead of minting a new one. Flag it: `⚠ opener/_NEXT mismatch — resume:_NEXT_NNN's moves [X] differ from opener's [Y]`, state which set you'll act on, and surface it before doing work.
2. Read `<system-dir>/_LOADUP.md` — context bootstrap: system architecture, map, retrieval index, operational tools.

## RESUME-WITH-VERIFICATION (after reading the `_NEXT`, before executing move 1)

A handoff is a **claim**, not a fact — verify it before acting (the fix for silent-dropout and booted-into-consumed-work; the *why* is in `_NEXT.md`). No DB, no agents — just `git` + `grep`.

**Step A — diff against the checkpoint.** If the header's `checkpoint:` is a SHA in a git repo, run `git -C <system-dir> diff --stat <checkpoint>..HEAD` for the ground truth of what changed since the handoff; if `n/a`/unresolvable, skip to grep-only and note `checkpoint unverifiable`.

**Step B — grep each move's Read-Map.** For every open move, inspect exactly the files/sections its `reads:` names (cross-check `skip:`) and classify it: **still-true** (target in the pre-move state, work genuinely pending) · **already-done** (target already holds the result, or diff shows it landed, or it's on `skip:` — do NOT execute) · **stale** (target moved/renamed/changed so the move no longer applies) · **unverified** (no `reads:` hint, or checkpoint unverifiable and grep inconclusive).

**Step C — report, then gate.** Emit one line per open move in the status block:
```
claimed: <move text>  /  verified: still-true | already-done | stale | unverified
```
All still-true → execute move 1 normally. Any **already-done**/**stale** → FLAG it, do NOT execute, name the next live move (or that the queue is exhausted). `unverified` is not a stop, but say so before acting.

**Step D — same-file-clobber check.** Derive the files move 1 will edit; read the `touched:` line of the other still-live slots (`<kit-dir>/bin/next-live.sh <system-dir>` for the live set, `grep -h '^touched:' <system-dir>/next/_NEXT_*.md` for their edit-lists). On an overlap, warn (`⚠ same-file overlap — _NEXT_NNN also touched <file>; a concurrent session may be mid-edit`) then proceed — advisory, not a block. Skip silently if no other slot is live.

## On demand only (pull when the task requires it)

Do NOT load these on boot. Pull only when the session task explicitly needs them.

*(List your on-demand files here with their trigger conditions — one row per file: the file, and the exact condition that should make a session pull it.)*

Use the retrieval index in `_LOADUP.md §4` to find anything else.

## Output (emit exactly this after reading — no prose, no preamble)

```
loaded: <every file actually read this boot, each with ✓ — e.g. _NEXT_017 ✓  _LOADUP ✓>
phase: [one phrase — current work mode]
tasks: N open  [or "tasks: none"]
verified: <checkpoint SHA or n/a> — <one claimed/verified line per open move>
  claimed: <move 1 text>  /  verified: still-true | already-done | stale | unverified
  claimed: <move 2 text>  /  verified: ...
next: [system] move N — <move text> (<model> / <effort>)
```

- `loaded:` — list every file you actually read this boot (the 2 always-load files + any on-demand pulls this session), each with ✓. This is the **proof-of-boot** line: a fresh session shows exactly what landed in context, so drift between "what boot should load" and "what got read" is visible at a glance.
- `tasks:` — read `<system-dir>/ledger/USER_TASKS.md` and count open items. Show count only; don't list them unless asked.
- `verified:` — the RESUME-WITH-VERIFICATION result (see the section above). Lead with the checkpoint SHA being diffed against (or `n/a`), then one `claimed: … / verified: …` line per open move. This is the **proof-of-contract** line: it shows the handoff's claims were checked against reality, not trusted blind. Omit only on a cold boot with no `_NEXT` loaded.
- Source `next:` from open moves in `_NEXT_NNN.md` (takes priority over _LOADUP §7). **Pick the first move that verified `still-true`** — skip any `already-done`, and surface any `stale` move rather than running it.
- If nothing pending: `next: nothing pending — what's the task?`
- If a move verified `already-done` or `stale`: do not silently execute it — flag it on its `verified:` line, then point `next:` at the first genuinely-live move (or `next: queue exhausted — all moves already-done; what's the task?`).

## What to never read on boot

*(List files too heavy or sensitive for every-session loading — design references, setup guides, raw source files, on-demand-only evidence.)*
