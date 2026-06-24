# _NEXT — Reference & Pointer (permanent spec — describes how handoffs work)

This file is the canonical spec for all `_NEXT_NNN.md` handoffs and tells a fresh boot where to find live session state. It is never used to store handoff content — only the spec.

**To boot:** use `/session N` to boot a specific file, or `/session` (no arg) to auto-pick the lowest-numbered un-consumed file with open moves. All handoffs live in `<system-dir>/next/`.

- These are **parallel session slots**, not a linear version history. A higher-numbered file is another concurrent session's handoff, not a newer version of yours — never assume "highest = latest state."
- If no file is named, `/session` auto-picks the **lowest-numbered un-consumed file with open moves** — never the highest. A `_NEXT_NNN.consumed` sidecar marks a done session; skip those.
- If the named file is missing, flag it.

---

## What _NEXT files are

Each numbered file is a frozen snapshot of where one session ended — a parallel slot, never edited after creation (treat it like a commit; corrections go in a *new* file, never a rewrite). All slots live in `<system-dir>/next/` — one folder, no archiving sweep.

---

## Format (line-1 title + header block + 3 sections)

```
# _NEXT_NNN — <focus label>    ← line 1; YOU write `# __FOCUS__ <3–6 word label>` and next-write.sh stamps the number

outcome: SUCCEEDED | PARTIAL_PLUS | PARTIAL_MINUS | FAILED    ← verdict on the session handed off (UNKNOWN optional; see below)
touched: <files this session edited, space-separated relative paths>    ← "none" if no edits; the next boot's same-file-clobber check reads it
checkpoint: <git short-SHA at handoff>   ← stamped by next-write.sh in a git repo; "n/a" if not a repo

worked: [strategies that worked this session — one per line; omit the section if none worth carrying]
failed: [attempts that failed + the one-line why — so the next session doesn't re-try them; omit if none]

## Pending
[in-flight work only — tasks started but not done; "none" if clean]

## Next moves
[2–4 strictly ordered actions: "N. [system] action — Model / effort"]
[each move carries a Read-Map: "   reads: <exact file:section the next session must open before this move>"]
[Skip-List: "   skip: <already-done items the next session must NOT redo>" — optional, per move or once at the end]

## Push to _LOADUP
[facts settled THIS session that _LOADUP §2 doesn't know yet]
[delete this section next pass after pushing to _LOADUP]
```

---

## The Verified Handoff — why these fields exist

A handoff is not a trusted note; it is a **checked contract**. The header block makes the claims the next boot verifies against reality (the RESUME-WITH-VERIFICATION pass in `boot.md` / `session.md`):

- **`outcome:`** — the session's own verdict: `SUCCEEDED` (all booted moves done), `PARTIAL_PLUS` (most done, a remainder carried — net forward), `PARTIAL_MINUS` (some progress, bulk still open — net stalled), `FAILED` (the planned work did not land); `UNKNOWN` only when genuinely unverifiable. This is the calibration signal — a verdict recorded *with* its work so the next boot can check claim against reality. The `PARTIAL_PLUS`/`PARTIAL_MINUS` split feeds greppable calibration-miss detection: `grep PARTIAL_MINUS next/` surfaces high-conviction calls that quietly stalled, instead of a flat `PARTIAL` laundering a soft-fail as progress.
- **`touched:`** — the files this session edited (space-separated relative paths; `none` if no edits). The next boot cross-checks its own intended edits against recent slots' `touched:` lists and warns on a same-file overlap — the zero-infra same-file-clobber guard (a real lock is deferred to scale).
- **`checkpoint:`** — the git short-SHA at handoff time. The next boot diffs `<checkpoint>..HEAD` to see what actually changed since the claims were written. `n/a` outside a git repo (verification falls back to grep-only).
- **`worked:` / `failed:`** — the strategy memory. `worked:` carries forward what to lean on; `failed:` is the do-not-retry list (each with its one-line why). Both optional — omit a section with nothing to say rather than writing "none".
- **`reads:` (per move)** — the Read-Map: the *exact* files/sections the next session must open before starting that move. This is what the boot grep-checks to confirm the move is still-true (not already-done, not stale).
- **`skip:`** — the Skip-List: items already finished, so the next session does not redo them. Guards the booted-into-consumed-work failure.

---

## Rules

**Pending** — only genuinely in-flight work (half-written file, mid-build script). Not a wishlist.

**Next moves** — strictly ordered (1 first, 2 second). If two moves could run in parallel, pick one first — never leave ordering ambiguous. Be specific: name the file, the action, the model tier.
  - Format: `N. [system] action — Model / effort`
  - Systems: `[infra]`, etc. — tag by subsystem of your project
  - Effort: `low` / `medium` / `high` / `max` / `ultra`

**Push to _LOADUP** — facts that belong in stable reference but haven't been written there yet.
  Self-destructs: next session that touches _LOADUP, move these lines in and delete this section.
  Do NOT copy facts already in _LOADUP §2 — that's double-storage.

**What not to include:**
  - Architecture or system design → that's `_LOADUP.md` and `README.md`
  - Facts already in stable reference docs
  - Completed tasks → log in `ledger/CHANGELOG.md`
  - Keep the whole file under 30 lines

---

## How _NEXT files are created

`<kit-dir>/bin/next-write.sh <system-dir> <content-file>` — picks the next free number and writes `_NEXT_NNN.md` into `<system-dir>/next/`. Collision-safe: if a concurrent session grabbed the same slot, it bumps to the next free number. **Focus label:** if the content file's line 1 is `# __FOCUS__ <label>`, the script rewrites it to `# _NEXT_NNN — <label>` (stamping the resolved number); with no sentinel, the file is copied verbatim (backward-compatible).

Numbers are unlimited and auto-expand: 001–999 (3 digits), 1000–9999 (4), etc.
