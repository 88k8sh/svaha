# /handoff — Session Wrap

Execute immediately, no preamble. Do not ask for confirmation.

**Alias:** saying **"svaha"** as a *close* (work done, nothing pending — per `CLAUDE.md` "## Boot" position rule), or **"that's it"** / "wrapping up" / "done for now", is the user's keyword for this command — the closing counterpart to the svaha-boot. The closing svaha is their **input**; the assistant echoes the **स्वाहा** seal (output) only once this handoff actually completes.

## Pre-flight check (do this before any other step)

Scan the session for ambiguities that would force a follow-up in the next session — specifically:
- **Multiple open threads with no clear priority** (two loops, two parallel workstreams, two competing next actions)
- **Missing information** that the next session would need to ask for (e.g. a decision unmade, a file path unknown)

If any such ambiguity exists, **ask the clarifying question NOW, before writing anything.** Wait for the answer, then proceed with the handoff. Do not write a handoff that embeds the question — that forces a second loop and defeats the purpose.

If no ambiguity: proceed directly, no preamble.

## Warrant gate (decide handoff vs. reflect-only)

Before running the steps below, check whether a full handoff is warranted. It is warranted only if **at least one** of these is true:
- There is genuinely in-flight work (started but not done) — **including shippable edits made this session that are still uncommitted/unpushed in a repo: an edit isn't *done* until it's committed and pushed, so do NOT downgrade to a reflection while the session's own changes sit uncommitted. A user-gated push doesn't make the work landed — it makes the push a `USER_TASKS` item *and* leaves the work live in-flight, which warrants the handoff and its seal.**
- There are queued next moves worth carrying forward

**Context size is NOT a warrant condition.** Heavy context is a *reboot* signal ("start fresh"), never a handoff trigger on its own — a session can fill context by *reading* (a big file, a long or unarchived/old conversation) while producing nothing to carry forward. If the only thing that's "high" is the context and there is no live in-flight work or queued move, do **not** mint a `_NEXT` — downgrade to reflection and reboot.

**The "would be lost" test for queued next moves (apply this before counting one).** A next move warrants a handoff *only if it is actionable work that would be lost without the `_NEXT`.* A **dormant state or watch-item already durably captured in a source file** (a rule in `CLAUDE.md`, an entry in a log, a conditional that `/audit` fires on its own) does **not** count — it isn't lost, it's already written down, so re-stating it in a `_NEXT` manufactures a phantom queue. Tests that fail this bar: "activate X when the user says so" (a state in `CLAUDE.md`), "watch for the next over-fire" (already in the over-fires log + `/audit`), "remember that we decided Y" (belongs in `_LOADUP`/CHANGELOG). If every "move" you can name is something a future session would *re-discover by reading a source file*, there is no real queue — downgrade to reflection.

**If none apply** (light session, nothing pending, no queue) a handoff would be pointless — **downgrade to a reflection.** Run only `reflect.md`'s `## Steps` (memory pass) and `## Bug log step`, emit the context-gauge line, append `handoff not needed — ran reflection instead [light/clean: nothing in-flight, no queue]`, give the bottom line, then close with the **reflection-banner** — `# ◇ ◇ ◇` framed by a full-width horizontal rule above and below, the grand *hollow* sibling of the `# स्वाहा` seal-banner (step 6): hollow = nothing carried forward; it marks a *reflection* close, never a checkpoint — the **soft** close: no `_NEXT` was frozen, so it forces no reboot (the user may keep going or stop), in contrast to the स्वाहा seal that captures a resume-thread and points to a fresh session. Then stop. Do **not** write a `_NEXT` file, do **not** emit the `Next session:` closer (there is no live slot to name), and do **not** run reflect's `## Handoff check` section — you are already inside a handoff, so re-running it would loop. (This is the mirror image of reflect's reflect→handoff escalation; the two commands share this one gate.)

**If warranted**, proceed through the steps below. The gate has already confirmed a `_NEXT` is needed, so step 2 writes one unconditionally.

## Steps

1. Emit the context gauge line:
   `context: ~<light|medium|heavy>  ·  <continue | wrap up soon | start fresh>  ·  next: <Sonnet|Opus> / <low|medium|high|max|ultra>`

2. **Write the `_NEXT` file.** (The Warrant gate above already confirmed one is needed — if it hadn't, you'd have downgraded to a reflection and never reached this step.) **Focus label:** make line 1 a 3–6 word label of the session's dominant thread (the thing move 1 continues), written as the sentinel `# __FOCUS__ <label>` — `next-write.sh` rewrites it to `# _NEXT_NNN — <label>` once it knows the slot (don't write the number yourself; a concurrent session may grab it). Then a blank line, the **header block** (outcome / checkpoint / worked / failed), then the 3 sections. Use this exact format (kept byte-identical to the spec in `_NEXT.md` — if you change one, change both):

   ```
   # __FOCUS__ <3–6 word focus label>   ← next-write.sh stamps the number → "# _NEXT_NNN — <label>"

   outcome: SUCCEEDED | PARTIAL_PLUS | PARTIAL_MINUS | FAILED   ← (UNKNOWN optional, if genuinely unverifiable)
   touched: [files this session edited, space-separated relative paths — "none" if no edits]
   checkpoint: __CHECKPOINT__            ← leave this literal sentinel; next-write.sh stamps the SHA (or "n/a")

   worked: [strategies that worked this session — one per line; omit the line if none worth carrying]
   failed: [attempts that failed + the one-line why — so the next session doesn't re-try them; omit if none]

   ## Pending
   [in-flight work only — tasks started but not done; "none" if clean]

   ## Next moves
   [2–4 ordered actions, each on one line: "N. [system] action — Model / effort"]
   [under each move, a Read-Map line: "   reads: <exact file:section to open before this move>"]
   [optional Skip-List: "   skip: <already-done item the next session must NOT redo>"]

   ## Push to _LOADUP
   [facts settled THIS session that _LOADUP §2 doesn't know yet; delete this section next pass after pushing]
   ```

   **Header block — the Verified Handoff contract.** These fields turn the handoff from a trusted note into a checked one — the next boot's RESUME-WITH-VERIFICATION pass (`boot.md` / `session.md`) verifies each claim against reality before executing move 1. **Field semantics are canonical in `_NEXT.md` (`## The Verified Handoff — why these fields exist`) — read them there, don't restate here.** Quick reference, set honestly as you write:
   - **`outcome:`** — `SUCCEEDED` / `PARTIAL_PLUS` (net forward) / `PARTIAL_MINUS` (net stalled) / `FAILED` (`UNKNOWN` only if unverifiable). The PLUS/MINUS split makes a stalled high-conviction call greppable as a calibration miss (`grep PARTIAL_MINUS next/`) — set it honestly, not to inflate.
   - **`touched:`** — every file this session edited (the same-file-clobber guard; an omission re-opens the gap).
   - **`checkpoint:`** — leave the literal `__CHECKPOINT__` sentinel; `next-write.sh` stamps the real SHA (or `n/a`). Don't hand-type a SHA.
   - **`worked:` / `failed:`** — strategy memory (lean-on list / do-not-retry list); omit either if empty, don't pad with "none".
   - **`reads:` per move** — the exact files/sections to open before the move; the boot pass grep-checks these. A move with no `reads:` can only be marked `unverified`.
   - **`skip:`** — anything already finished the next session must not redo (the guard against booting into consumed work).

   **Continuity check (before you finalize moves):** diff the moves you're about to write against the `## Next moves` of the `_NEXT` you booted from. Any of those that is **neither completed this session nor carried forward** is being *dropped* — never let it vanish silently (a live move can otherwise fall out of `_NEXT` for many sessions, then resurface behind a false "standing since" line). For each dropped move, do one and say which in your turn: carry it forward, promote it to `USER_TASKS.md` if it actually needs the user (per CLAUDE.md "Surface what's slipping"), or state explicitly that you're dropping it and why. Match on the move's *intent*, not exact wording — a reworded move is still the same move.

   **Move quality (cold-reader test + resolution triggers + Read-Map).** Before finalizing, read move 1 as a *cold reader who wasn't in this session*: is it specific enough to start immediately — naming the file, the action, and the first concrete step? "Continue the work" fails; "write the X spec in `path` starting from the Y decision" passes. Rewrite any move that wouldn't survive a cold read. **Attach a `reads:` line to every move** — the exact file(s)/section(s) the next session must open before starting it; this is both the cold-reader's map and what the boot's RESUME-WITH-VERIFICATION pass grep-checks to confirm the move hasn't gone stale or already-done. A move with no `reads:` can only be marked `unverified` at next boot. And any **Pending** or blocked item must name its **resolution trigger** — the event, file, or decision it's waiting on (what *unblocks* it), not just that it's stuck. An open item with no trigger is a dead end the next session can't action.

   Run `<kit-dir>/bin/next-write.sh <system-dir> <temp-file> [--consume NNN]` — auto-increments and writes into `<system-dir>/next/` (e.g. `<system-dir>/next/_NEXT_018.md`). **If this session booted from `_NEXT_NNN.md` (via `/session N`), pass `--consume NNN`** (the booted-from slot, zero-padded): `next-write.sh` writes + checkpoint-stamps the new slot, *then* retires NNN — mint-and-retire as one atomic act (see Consumed stamp below). All handoffs live in one folder; no archiving sweep. This covers all work touched this session: infra, content, etc. Report the filename written.

   **Consumed stamp (atomic with the mint — consume-leak fix, layer A):** retiring the booted-from slot is no longer a separate hand-typed `touch` you can forget — it rides the `--consume NNN` flag on the `next-write.sh` call above. `next-write.sh` writes + checkpoint-stamps the new slot, confirms it is non-empty, *then* calls `bin/next-consume.sh` to stamp `_NEXT_NNN.consumed` — so the predecessor is never retired before its successor exists, and you cannot mint a successor while forgetting the predecessor. (`next-consume.sh` is idempotent and records when+why into the sidecar, so every retire is auditable.) Pass `--consume NNN` whenever you booted via `/session N`. Omit it only when booted cold (no `_NEXT` at boot) or under the ride-forward exception (zero progress → no new slot minted → nothing to retire).

   **Supersede stamp (consumption is completion-coupled, not only boot-coupled):** the consumed stamp above retires only the file you *booted from*. But work also gets finished or rendered moot **outside** that path — a session supersedes an *older* slot it never booted from, finishes work cold, or closes via a reflection (which never reaches this step). Those slots then sit **falsely live forever**, because `_NEXT` files are frozen so their move-text always parses as open and `next-live.sh --check` cannot see it. So before finishing: run `<kit-dir>/bin/next-live.sh <system-dir>`, read the live set, and for **any *other* live `_NEXT_MMM` whose moves THIS session completed or rendered moot**, retire it with `<kit-dir>/bin/next-consume.sh <system-dir> MMM "done: <one-line why>"` (the reason is recorded into the sidecar) + a one-line CHANGELOG note naming which and why. **Judgment-gated:** stamp only a slot you can *name* as genuinely done/superseded — never a blanket sweep, and never one merely deferred (only a human tells deferred from dead). If you miss one here, `next-live.sh`'s DONE-PROBABLE flag catches any live slot the CHANGELOG marks done — but stamping it at the source is cleaner.

   **Read-back:** immediately read the written file and confirm it is non-empty. If the file is missing or empty: halt, report the failure, do not proceed to step 6. A tool returning "success" is not confirmation — only the file's content is.

   **Git commit (if repo):** check `git -C <system-dir> rev-parse --git-dir 2>/dev/null`. If `<system-dir>` is a git repo: `git -C <system-dir> add next/_NEXT_NNN.md && git -C <system-dir> commit -m "handoff: _NEXT_NNN"`. Skip silently if not a git repo. **`git push` is a knowing opt-in, not automatic** — it is the loop's one outbound action (to *your own* user-configured remote, your backup), so leave it out by default and run it yourself, or add ` && git -C <system-dir> push` to the line above only if you've deliberately chosen to back the handoff up off-machine. (Local-first by default; the push is git-native and fully vettable, but it's still the only place the loop reaches off the box, so it stays your call.)

3. **User tasks** — scan the session for items that belong in `<system-dir>/ledger/USER_TASKS.md`. Apply this test before adding anything: **"Can the assistant execute this by reading files and writing?"** If yes → `_NEXT` move, not USER_TASKS. USER_TASKS is only for: (a) physical actions requiring the user's hands/credentials (password manager, hardware wallet, Finder drag from denied path), (b) life/personal decisions the assistant cannot make on the user's behalf, (c) find-and-retrieve where the user holds the material in another app or their memory. Architecture tasks, synthesis passes, system rewrites, and Opus-level reasoning jobs are all _NEXT — not USER_TASKS, even if they're large or complex. For each new USER_TASKS item, append under `## Open`. For items completed this session, move to `## Done` with date. Skip if nothing changed.

4. **Bug log** — run the bug-log pass exactly as specified in `~/.claude/commands/reflect.md` ("## Bug log step"): append fixes to `<system-dir>/ledger/session-fixes.md` in that format; skip if nothing was caught and fixed. **`reflect.md` is the single source of truth for this logic — do not restate the format here, so the two can't drift.**

5. **Memory reflection** — before writing the session closer, run the memory pass exactly as specified in `~/.claude/commands/reflect.md` ("## Steps"): the scan targets, the 2-part bar, and the auto-skip rules. **`reflect.md` is the single source of truth for this logic — do not restate the bar or auto-skip rules here, so the two can't drift.**

6. If a `_NEXT` file was written, confirm it exists and emit the next-session closer. Skip this step if no `_NEXT` was written (light/clean session).

   **File invariant (hard gate):** the `/session NNN` number MUST name an existing `<system-dir>/next/_NEXT_NNN.md` whose `## Next moves` are **live** (not already done) — never a spec, living doc, or README. Normally that's the file you **wrote this session in step 2** and confirmed in the read-back. **Hard ban: never point the closer at a *consumed* `_NEXT`** (one whose moves are finished, or that carries a `_NEXT_NNN.consumed` sidecar) — recycling a consumed number boots the next session into completed work. **Ride-forward exception:** if this session made *zero progress* on the `_NEXT` it booted from, generated no new moves, and settled nothing, do **not** mint a duplicate snapshot of an identical queue — skip the step-2 write and its consumed stamp, and re-point the closer at that *same still-live* file (the boot-side mismatch guard + the `resume-line-guard.sh` consumed-check backstop this). If step 2 wrote no `_NEXT` and there is no live file to ride, do not emit a closer.

   Append the focus label (from the file's line-1 header) after the number so the next chat's title is legible. The handoff turn then ends with the standard end-of-turn bottom line, and the session seal — स्वाहा — sits in the **seal-banner** at the very foot of the turn, framed by a full-width horizontal rule (`---`) above and below (the handoff is the sealing act; *svāhā* = "it is accomplished"; the rules are block elements the renderer pads around, so the seal stands alone in its own band — a grand, unmissable ending). So the close runs: closer → bottom line → seal-banner. The banner sits well clear of the `Next session:` line `resume-line-guard.sh` reads — never prefix that line, or the hook misses the match.

   **First-seal teaching note (one-time, newcomers).** The *first* time you ever emit the seal for a system — detectable when `<system-dir>/next/` holds only the seed `_NEXT_001.md` plus the `_NEXT` you wrote this session — insert one italic line **between the bottom line and the seal-banner** (so the seal still lands as the foot of the turn), explaining the user's first sight of the word: *(First handoff — so the seal makes sense: the स्वाहा just below is your receipt that this session's work is now written to file. You'll see it at every sealed handoff, and only then.)* Emit it **once** — omit it on every later handoff; the seal stands alone thereafter. (This is the *earned* version of the first-session magic — the word answers back where it actually means something, not on a cold open where nothing's been recorded yet.)

   ```
   Next session: /session NNN — <focus label>

   Bottom line: <session-end status>

   ---

   # स्वाहा

   ---
   ```

## What _NEXT files are

`_NEXT` files are **both operational and archival**. Each one is a frozen snapshot of where a session ended — a parallel session slot, never edited after creation. All slots live in `<system-dir>/next/`. Treat each file as a permanent record of that session, not a throwaway queue item.

## _NEXT content rules

- **Header block** (`outcome` / `checkpoint` / `worked` / `failed`) = the Verified-Handoff contract the next boot checks. `outcome` is your honest verdict on the session; `checkpoint` is stamped by `next-write.sh` (leave the `__CHECKPOINT__` sentinel); `worked`/`failed` are optional strategy memory — omit either if empty.
- **Pending** = only genuinely in-flight work (a file half-written, a script mid-build). Not a wishlist.
- **Next moves** = only moves that **emerged from THIS session's work** — new tasks identified, or work genuinely started and left incomplete. Do NOT harvest moves from prior frozen _NEXT files. If something sat in _NEXT_004 and wasn't touched this session, leave it there — it stays frozen and searchable, not re-copied here. Also do not include moves already completed this session. Each move carries a `reads:` line (its Read-Map — the exact file/section to open before starting it; the boot verification pass checks this). Optionally append `(requires: filename)` to a move that needs an on-demand file pre-loaded on boot — e.g. `1. [system] audit log — Opus / max (requires: <file>)`. `/session` reads this annotation and pre-loads the file before starting move 1. (`requires:` pre-loads on boot; `reads:` is the per-move map the verification pass greps — they can name the same file.)
- **Push to _LOADUP** = facts that belong in the stable reference but haven't been written there yet. This section self-destructs: on the next session that touches `_LOADUP`, move these lines into `_LOADUP §2` and delete the section.
- Do NOT copy "Settled — don't re-derive" facts that are already in `_LOADUP §2`. That's double-storage.
- Keep the whole file under 30 lines.

## What not to include

- Architecture, system design, or how the system works — that's `_LOADUP`
- Facts already in `_LOADUP §2` — don't re-copy them
- Completed tasks — log in `ledger/CHANGELOG.md`, not here
