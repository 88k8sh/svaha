---
id: loadup
created: <date>
updated: <date>
source: doc
load_priority: boot
layer: meta
summary: Read-me-first context bootstrap — fast path, map, retrieval index, operational tools.
status: living
---

# _LOADUP — Context Bootstrap (read me first)

> **Goal: a fresh chat reaches ~full context in a handful of files instead of hundreds.**
> **This is a template.** Replace every `<fill-in>` and bracketed placeholder with your project's specifics, then delete this line. The §0–8 skeleton is the contract — keep the section structure even as you swap the content.

## 0. System architecture (settled <date>)

*State the one-paragraph shape of your system here: what the root directory is, what the major subtrees are, how many boot sequences and handoff pools exist. Keep it to the structural truth a new session needs before it reads anything else.*

One unified system. `<system-dir>/` is the root. One boot sequence, one handoff pool (`<system-dir>/next/`).

*Example fill-in:* `<system-dir>/` is the root; <subsystem> lives at `<system-dir>/<subsystem-path>/`. "Boot <mode>" is a lightweight alias that skips `_LOADUP.md` for <mode> sessions.

## 1. The fast path — full context in N reads, in order

Boot reads the specific `_NEXT_NNN.md` named in the opener block (or auto-picked by `/session`) first, then:

1. **this file** (`<system-dir>/_LOADUP.md`) — the map + index
2. *(add your next always-load file here — e.g. a core reference doc the session needs every time)*
3. *(add further always-load files in read order; keep this list short — heavy/rare files belong in §6, not here)*

→ After these you are **~90% caught up.** Everything else is reference, pulled on demand via §4 / §6.

## 2. Settled system facts — do NOT re-derive

*Add settled facts here as the system matures. Each fact saves a re-derivation per session: canonical paths, installed tools, known aliases, resolved bugs, environment quirks. Keep behavior rules OUT of this section — those live in `CLAUDE.md` (see the content-placement table there).*

- **`<kit-dir>/bin/next-write.sh`** writes new handoffs to `<system-dir>/next/`; collision-safe (bumps to the next free slot if a concurrent session grabbed it); unlimited numbering. `_NEXT_NNN.md` files are **parallel session slots** — boot reads the file specified by `/session N` (or auto-picks the lowest with open moves via `/session` no-arg), NOT the highest number.
- **`bin/coherence-check.py --boot`** runs a structural integrity check at boot; **`--stop`** runs an exit check wired as a Stop hook in `settings.json`.
- **`_NEXT.md`** = permanent reference & pointer (spec + boot instructions); never overwritten.
- **`_NEXT_NNN.md` files are frozen once written** — corrections go in a new numbered file, never a rewrite.
- **Registered slash commands** at `~/.claude/commands/`: `<list your commands — e.g. /boot, /session, /handoff, /reflect, /audit, /foldin>`.
- *Example fill-in:* `<tool>` installed for `<purpose>`; `<alias>` added to `~/.zshrc`; `<known OS/sandbox quirk>` = expected, not a bug.

## 3. The map (what lives where)

| Path | What | Read tier |
|---|---|---|
| `<system-dir>/_NEXT.md` | Permanent handoff spec + pointer | always (boot) |
| `<system-dir>/next/` | All session handoffs (parallel slots) | always (boot — named file only) |
| `<system-dir>/ledger/CHANGELOG.md` | Master system log — every structural change | reference |
| `<system-dir>/ledger/USER_TASKS.md` | Persistent to-do list — things only a human can do (physical actions, decisions, find-and-retrieve) | reference |
| `<system-dir>/ledger/session-fixes.md` | Bugs caught + patched per session — failure modes for future reference | reference |
| `<system-dir>/ledger/DECISIONS.md` | Design decisions + alternatives considered (the road not taken) | reference |
| `<system-dir>/ledger/LESSONS.md` | Named lessons distilled from incidents — consolidated, human-readable | reference |
| `<system-dir>/ledger/drift-guard-evidence.md` | Running log of instances where the drift-guard hook caught real drift | reference |
| `<system-dir>/_ARCHIVE/` | Graveyard for superseded files — move here, never hard-delete | reference |
| *(add your own content subtrees here — e.g. `<system-dir>/<domain>/` → what it holds → read tier)* | | |

## 4. Retrieval index (concept → location)

*Fill in as your project accumulates reference material. The point of this section is "where do I find X" answered once, so no session re-derives it. Format: concept → file. Group by whatever axis fits your material (by topic, by domain, by document type).*

- **By topic:** `<topic>` → `<file>` · `<topic>` → `<file>`
- **By domain:** `<domain>` → `<path>` · `<domain>` → `<path>`
- *(extend with your own axes; point at an index file rather than re-listing if one exists)*

## 5. Operational tools (run on demand, not during sessions)

*List the scripts a session invokes by hand. Keep one line each: command → what it does.*

- `python <kit-dir>/bin/coherence-check.py --boot` → structural integrity check
- `bash <kit-dir>/bin/next-write.sh <system-dir> <content-file>` → write the next handoff
- *(add your own: backfill/tagging scripts, bundle builders, re-rank passes, etc.)*

## 6. On-demand files (pull only when the task requires it)

*List files too heavy or rare to load every boot but frequently needed. Order by operational urgency — most immediately actionable first, deepest reference last. Format: file → when to pull.*

| File | When to pull |
|---|---|
| `<system-dir>/SYNC_MAP.md` | Before any structural edit (paths, schemas, boot/handoff loop, command files) |
| `<file>` | `<the specific trigger condition that justifies the read>` |
| `<file>` | `<trigger>` |

## 7. Boot status format (output exactly this — no sub-bullets, no prose)

```
loaded: <every file actually read this boot, each with ✓ — e.g. _NEXT_017 ✓  _LOADUP ✓>
phase: [one phrase — current work mode]
tasks: N open  [or "tasks: none"]
verified: <checkpoint SHA or n/a> — one claimed/verified line per open move
  claimed: <move text>  /  verified: still-true | already-done | stale | unverified
next: [system] move N — <move text> (<model> / <effort>)
```

- `loaded:` is the **proof-of-boot** line — every file actually read this boot (the always-load set + any on-demand pulls), each ✓. Makes "what boot should load" vs "what got read" visible at a glance.
- `verified:` is the **proof-of-contract** line — the result of the RESUME-WITH-VERIFICATION pass (canonical procedure in `boot.md`). It diffs the `_NEXT` header's `checkpoint:` SHA against `HEAD` and grep-checks each move's `reads:` hint, so the handoff's claims are checked against reality before move 1 runs. One `claimed: … / verified: …` line per open move. Omit only on a cold boot with no `_NEXT`.

**`next:` line rules:**
- Source from open moves in `_NEXT_NNN.md` (takes priority over §6 on-demand edges). Pick the first move that verified `still-true`; skip `already-done`, surface `stale` rather than running it.
- Use `next: nothing pending — what's the task?` when `_NEXT` is absent or trimmed (or `next: queue exhausted — all moves already-done; what's the task?` when every move verified done).

*(If your system has a periodic check that should surface at boot — e.g. an audit-due or review-due nudge — append its one-line trigger here, conditional on the relevant file having been loaded.)*

## 8. Sync-map — coherence guard (tripwires)

**Full coupling table → `<system-dir>/SYNC_MAP.md`** ("change X → update Y"). It is the maintenance view; if you also keep a `SYSTEM_MAP.md` (data-flow view), keep the two reconciled.
Pull SYNC_MAP before any *structural* edit (paths, schemas, boot/handoff loop, command files). Below are the highest-blast-radius tripwires. Rows are independent; one edit can trip several.

| When you change… | Also update… |
|---|---|
| Which files boot loads (fast-path) | `_LOADUP §1` + `boot.md` always-load list + any boot-bundle script |
| Renumber `_LOADUP §N` | every `§N` pointer in `audit.md` / `boot.md` / `_NEXT.md` / `handoff.md` |
| Migrate/rename a top-level path | sweep every doc + memory + script + command file embedding the old root |
| Register a new slash command | add it to `_LOADUP §2` **and** `SYNC_MAP` |
| *(add couplings as your system grows — each one earns its place after an incident, not before)* | |

A `PreToolUse` drift-guard hook (`<kit-dir>/bin/drift-guard.py`, registered in `~/.claude/settings.json`) auto-surfaces the relevant couplings whenever a plumbing file is edited — a backstop, not a replacement for the full map.

**Rule of thumb:** after any structural edit, `grep -rn` the tree for the old name/path/field/count before closing the session.
