# /reflect — Memory Reflection

Execute immediately, no preamble. Do not ask for confirmation.

This is the **canonical** memory + bug-log pass. `/handoff` steps 4–5 delegate here (single source of truth — the logic lives only in this file). Run it standalone when you want just this pass: no `_NEXT` file, no context gauge, no session closer.

## When to use

- Session reached a natural conclusion with nothing left pending
- You want to capture something mid-session without a full handoff
- A stop hook triggered a lightweight reflection

## Steps

Scan the **user's messages** in this session for:
- New patterns in how the user thinks, works, or communicates
- Corrections to your behavior (things the user pushed back on or redirected)
- Confirmations of non-obvious approaches that worked
- New facts about the user's projects, preferences, or context not already in memory

Use AI responses only as context to interpret short or reactive user messages ("yeah do that", "no not like that").

For each finding:
1. Check `<system-dir>/memory/MEMORY.md` — if an existing memory covers it, update that file. If not, create a new memory file and add a pointer to `MEMORY.md`.
2. Skip findings already well-captured.
3. **Bar (both must pass):**
   - Would a future Claude behave differently after reading this entry?
   - Would that behavioral difference change the outcome of a real task in a meaningful way?
   If either fails, skip it.

4. **Auto-skip these regardless:**
   - One-time structural fixes (rule moved to CLAUDE.md, file renamed) — the fix is already done
   - Confirmations of things already in CLAUDE.md — memory shadowing CLAUDE.md is redundant
   - Pure meta-observations about the memory system's structure/architecture — those belong in CLAUDE.md or this skill
   - **But DO capture:** behavioral corrections about *how* to write memory entries (e.g., "don't over-generalize context-specific decisions into universal rules") — these pass through the bar test like any other correction.

Be specific — "user corrected X because Y" is useful; "user likes clarity" is not.

## Bug log step

After the memory pass, scan the session for **system bugs caught and fixed** — things Claude or the user identified as broken/wrong and corrected during the session (script logic errors, command referencing a stale path, wrong threshold, bad rule, etc.). For each bug:

Append to `<system-dir>/ledger/session-fixes.md`:

```
## YYYY-MM-DD — [one-line description]
- **Bug:** [what was wrong]
- **Fix:** [what was changed and where]
```

If nothing was caught and fixed, skip this step entirely — do not create a blank entry.

## Handoff check (standalone `/reflect` runs only)

**This section is NOT part of the logic `/handoff` delegates to** — `/handoff` borrows only `## Steps` and `## Bug log step` above. Skip this section entirely when reflect is being run *from inside* a handoff; run it only when `/reflect` was invoked directly. (This is what prevents a reflect → handoff → reflect loop.)

After the memory + bug passes, decide whether this session actually warranted a full handoff, using the **same Warrant gate as `/handoff`** (canonical: `handoff.md`'s `## Warrant gate` — do not restate its conditions here, so the two can't drift). In brief: a handoff is warranted only by **live carry-forward work** — genuine in-flight work or queued moves *from this session* that would be lost. **Context size is not a trigger** (a big conversation is a reboot signal, not a handoff one).

**If warranted:** emit `handoff suggested — running it`, then invoke `/handoff` directly. The memory + bug passes you just ran are idempotent, so handoff's delegated steps 4–5 will correctly find nothing new — no double-writing. Let handoff produce the gauge, `_NEXT` file, and session closer (`Next session: /session NNN`); do **not** also emit the reflect `## Output` line — handoff's output supersedes it.

**If not warranted:** emit the reflect `## Output` line, append `handoff not needed — [light/clean: nothing in-flight, no queue]`, then close with the **reflection-banner** (`# ◇ ◇ ◇` framed by a `---` rule above and below — the grand hollow sibling of the `# स्वाहा` seal; a reflection ran, so it still earns a banner, but hollow because nothing is carried forward). Do not run handoff.

## Output

After both passes (only when handoff was *not* run), emit one of:
- `reflect: N memories updated/created — [brief list]; M bugs logged`
- `reflect: N memories updated/created — [brief list]`
- `reflect: nothing new to capture`

That's it. No further summary needed.
