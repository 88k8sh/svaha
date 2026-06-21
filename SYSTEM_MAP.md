# SYSTEM_MAP — Data-Flow View

> Where everything lives and how it moves. This is the **data-flow** view of the kit.
> This file is the key; it answers "what file does what, and how does a session flow through them."
> Edit your mental model of the system → reconcile this file (and the coupling map, if you add one — see *Coherence* in `CLAUDE.md`).

---

## The two-file boot

Every session loads exactly two files, always — no more on boot.

| File | When | What it contains |
|---|---|---|
| `next/_NEXT_NNN.md` (named in the opener, or auto-picked by `/session`) | **Always** | Frozen snapshot of the prior session: pending work, next moves, facts to push up to `_LOADUP` |
| `_LOADUP.md` | **Always** | Stable reference: system architecture, this map, the retrieval index (`§4`), operational tools |

`boot.md` is the spec for the sequence; `session.md` is the smart entry point that picks the right `_NEXT` for you. After reading the two files, boot emits a **proof-of-boot line** (`loaded: _NEXT_NNN ✓  _LOADUP ✓ …`) so a fresh session shows exactly what landed in context — drift between "what boot should load" and "what got read" is visible at a glance.

Everything else is **on demand** — pulled only when the session task requires it, via the retrieval index in `_LOADUP.md §4`. Heavy or rarely-needed files are never read on boot.

---

## The handoff loop (session-by-session)

This is the spine of the kit — how state survives across sessions that otherwise share no memory.

```
  /session  or  /boot
      │  reads next/_NEXT_NNN.md (lowest-numbered with open moves, or named in opener)
      │  reads _LOADUP.md
      ▼
   ┌──────────┐
   │   work   │   ← the session does its thing
   └──────────┘
      │
      ▼
  /handoff   (Warrant gate: light + clean → downgrade to /reflect, write nothing)
      │
      │  if warranted:
      │   1. bin/next-write.sh  → mints a NEW frozen next/_NEXT_NNN+1.md (collision-safe auto-increment)
      │   2. memory/*.md        → behavioral rules for future sessions
      │   3. touch next/_NEXT_NNN.consumed   → marks the booted session done
      │   4. logs to 30_LEDGER/CHANGELOG.md  → structural digest
      ▼
  next session boots → reads the _NEXT just minted → loop closes
```

Key invariants this loop enforces:

- **`_NEXT_NNN.md` files are frozen.** Never edited, appended, or merged after creation. Missed something? Mint a *new* numbered file. Treat each like a commit.
- **`next-write.sh` owns the number.** The handoff writes a `# __FOCUS__ <label>` sentinel; the script stamps the real `_NEXT_NNN` slot once it knows which number is free. A concurrent session can't grab the same slot.
- **Numbers are parallel session slots, not versions.** A higher number is *another session's* handoff, not a newer copy of yours. `_NEXT_NNN.consumed` sidecars mark which slots are spent so `/session` never replays done work.
- **The "Push to `_LOADUP`" valve.** Each `_NEXT` has a `## Push to _LOADUP` section — the channel for operational facts to trickle up into `_LOADUP.md §2` (stable reference). It self-destructs: the next session that touches `_LOADUP` moves those lines up and deletes the section.

### The session pool (`next/`)

| File pattern | What it is |
|---|---|
| `_NEXT_NNN.md` | Frozen handoff — a parallel session slot, never edited after creation |
| `_NEXT_NNN.consumed` | Empty sidecar — marks a session as spent; `/session` skips it |
| `_NEXT.md` | The pool's permanent spec/pointer (not a handoff itself) |

`/session` (no arg) auto-picks the lowest-numbered open (unconsumed) session. `/session list` runs `bin/next-live.sh` — the **single source of truth** for the live set — never eyeball the folder, because concurrent handoffs mutate it underneath any hand-built list.

---

## Where each layer's files live

### Reference layer (stable, loaded on boot or on demand)
| What | Where |
|---|---|
| Stable facts, system architecture, retrieval index | `_LOADUP.md` (`§2` facts, `§4` index) |
| This data-flow map | `SYSTEM_MAP.md` |
| Design decisions + alternatives considered | `30_LEDGER/DECISIONS.md` *(optional — add if needed)* |
| Named lessons from incidents | `30_LEDGER/LESSONS.md` *(optional — add if needed)* |

### Behavioral layer (rules that govern how sessions act)
| What | Where |
|---|---|
| Universal behavior rules / guardrails | `CLAUDE.md` |
| Per-session behavioral corrections | `memory/*.md` (indexed by `memory/MEMORY.md`) |

### Ledger layer (audit trail — append-mostly)
| File | Written by | What it records |
|---|---|---|
| `30_LEDGER/CHANGELOG.md` | `/handoff` (or manually) | Structural changes — NEW, EDIT, MOVED |
| `30_LEDGER/session-fixes.md` | `/reflect` (via `/handoff`) | Bugs caught and fixed |
| `30_LEDGER/USER_TASKS.md` | `/handoff` | Actions only the human can take (hands, credentials, decisions) |
| `30_LEDGER/audit-state.md` | `/audit` | Counter: last audit, date, tier |
| `30_LEDGER/drift-guard-evidence.md` | Manual | Guard fires: real catches + false positives |
| `_ARCHIVE/` | Manual | Retired files — no hard deletes; supersede then archive |

### Command layer (the slash-command specs)
| File | Command | Role |
|---|---|---|
| `boot.md` | `/boot` | Two-file boot sequence + proof-of-boot line |
| `session.md` | `/session` | Smart entry: auto-pick, list, or boot a specific slot |
| `handoff.md` | `/handoff` | Session wrap — mints the next `_NEXT`, warrant-gated |
| `reflect.md` | `/reflect` | Memory pass + bug log — the lightweight wrap |
| `audit.md` | `/audit` | Periodic drift check across the whole tree |
| `foldin.md` | `/foldin` | One-time adoption of an ungoverned thread — reconstruct state, mint its first `_NEXT` |

---

## How the guard layer wraps the loop

The guardrails fire in a defined order — **prevention → entry → exit → periodic** — so drift is caught at every stage of a session, not just at the end.

| Guard | Stage | File | When it fires | What it does |
|---|---|---|---|---|
| `bin/drift-guard.py` | **prevention** | `bin/drift-guard.py` | PreToolUse — every structural file edit | Injects the relevant coupling reminder at edit-time, so a change to one plumbing file surfaces what to update downstream |
| `bin/coherence-check.py --boot` | **entry** | `bin/coherence-check.py` | On boot (or run via Bash) | Verifies boot-layer integrity: required files exist, the command set matches |
| `hooks/context-canary.sh` | **exit** | `hooks/context-canary.sh` | Stop / as the transcript grows | Emits the context gauge (KB estimate, light/medium/heavy) so you reboot before context bloats |
| `hooks/memory-reflect.sh` | **exit** | `hooks/memory-reflect.sh` | Stop | Tiered nudge to run `/reflect` before the session closes |
| `hooks/launchpad-nudge.sh` | **exit** | `hooks/launchpad-nudge.sh` | Stop (heavy sessions) | Reminds you to write `_NEXT` and boot from it next time |
| `hooks/resume-line-guard.sh` | **exit** | `hooks/resume-line-guard.sh` | Stop | Validates any `Next session: /session NNN` closer — confirms `next/_NEXT_NNN.md` actually exists, flagging placeholder or recycled numbers before they propagate |
| `bin/next-live.sh --check` | **periodic** | `bin/next-live.sh` | Run on demand / by `/audit` | Reports `.consumed` desyncs (`DONE-UNCONSUMED`, `ORPHAN`) in the session pool |
| `/audit` | **periodic** | `audit.md` | Every few sessions | Full drift sweep: unpushed facts, contradictions, carry-forward debt |

In-session guardrails (defined in `CLAUDE.md`, no hook needed) wrap the loop from the *decision* side rather than the file side: the **confirmation gate** (two lists — pre-authorized vs. always-stop), the **model-fit check** (entry-side model match), the **direction-clarity** and **auto-continue** rules, the **conviction tag** with its weigh-before-ask discipline, and the **auto-handoff** trigger that fires `/handoff` the moment the gauge hits "wrap up soon" or the user signals session end.

The two views fit together: hooks guard the *files and plumbing*; the `CLAUDE.md` rules guard the *judgment calls*. Together they catch drift both when you pick up a task and when you finish one.

---

## What's pending / not yet built

| Item | Status |
|---|---|
| *(add items here as your system grows — completed scaffolding lives in `CHANGELOG.md`, not here)* | |
