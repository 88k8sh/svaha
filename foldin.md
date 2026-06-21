# /foldin — Adopt an Ungoverned Session

Execute immediately, no preamble. Do not ask for confirmation.

**What this is for.** A one-time migration: pull a conversation that has been running *without* the handoff system into it. Use `/foldin` **once** per thread — to reconstruct its state, capture what it decided, and mint its first `_NEXT`. After that, the thread uses `/handoff` for every subsequent wrap.

**How it differs from `/handoff`.** `/handoff` assumes the session already operated under governance — it just wraps. `/foldin` assumes it did **not**: it adds explicit state-reconstruction, a spine cross-check, and decision extraction that `/handoff` takes for granted. If this session already booted from a `_NEXT` (i.e. it's already governed), you don't need `/foldin` — run `/handoff` instead and say so.

---

## STEP 1 — Reconstruct this thread's state (from context, no file reads yet)

Answer each, specifically — "continue the work" is not an answer; name the file, the decision, the concrete next step:

1. **What is this thread?** Project + workstream + one line on what it's doing.
2. **Most important thing in progress or blocked** right now.
3. **Decisions made in this chat not yet saved anywhere** — with the alternatives weighed, if recoverable.
4. **Dead ends hit and why they were rejected.**
5. **Open items waiting on the user** (decisions, credentials, physical actions).
6. **Files created or modified** this session — with paths.
7. **The single next action** the next session should start with (must pass the cold-reader test — see Step 5).

Output as a numbered list.

## STEP 2 — Cross-check against the spine

Read `<system-dir>/_LOADUP.md` (and any `_NEXT_NNN.md` already in context for this thread). Compare your Step-1 reconstruction against it.

**Flag every conflict — do not resolve silently.** List each as `⚠ conflict: [Step-1 claim] vs [spine says X]` for the user to adjudicate. If none: state `no spine conflicts`.

## STEP 3 — Extract decisions → DECISIONS.md

From this chat, identify every significant decision that weighed alternatives and chose. Append each to `<system-dir>/30_LEDGER/DECISIONS.md` in that file's format (`Chose / Over / Why`). If a decision's reasoning can't be reconstructed from context, record the decision and write `reasoning not recoverable from context`. Do not filter — record all; the user decides what matters.

## STEP 4 — Route user-action items → USER_TASKS.md

Apply the USER_TASKS test (per `handoff.md` step 3 — can the assistant execute it by reading/writing? if yes it's a `_NEXT` move, not USER_TASKS). Append genuine user-action items under `## Open` in `<system-dir>/30_LEDGER/USER_TASKS.md`.

## STEP 5 — Mint the first `_NEXT` for this thread

Write the `_NEXT` exactly as specified in `~/.claude/commands/handoff.md` step 2 — same `# __FOCUS__ <label>` sentinel, same 3-section format (`## Pending` / `## Next moves` / `## Push to _LOADUP`), same `bin/next-write.sh <system-dir> <temp-file>` call, same read-back. **`handoff.md` is the single source of truth for the write mechanics — do not restate them here, so the two can't drift.** Apply the move-quality bar: every move passes the **cold-reader test** (specific enough that someone with no memory of this chat could start move 1), and every blocked item names its **resolution trigger**.

There is no `_NEXT` to mark consumed (this thread had none) — skip the consumed stamp.

## STEP 6 — Confirm migration complete

Emit:

```
FOLD-IN COMPLETE — <project/thread>
decisions recovered: N   ·   dead ends recorded: N
files identified: <list or none>
conflicts flagged: N   ·   user tasks added: N
_NEXT written: <system-dir>/next/_NEXT_NNN.md ✓ (read-back confirmed)

Next session: /session NNN — <focus label>
```

From here this thread is governed — use `/handoff` for all future wraps, never `/foldin` again.
