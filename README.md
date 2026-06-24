<div align="center">

# Svaha

### Claude Code that learns from its own track record.

One `CLAUDE.md` + a small scaffold turn the loose pieces of a good Claude Code setup into **one self-calibrating loop**: a decision is made *with its conviction*, recorded in the handoff *with its outcome*, and verified against reality at the next boot — and a call that didn't pan out becomes a rule that retunes how the next one gets made. Continuity feeds coherence feeds better decisions feeds continuity.

[The behavior contract](CLAUDE.md) · [Credits](docs/CREDITS.md) · MIT

</div>

---

> **New here?** Open **[`start.html`](docs/start.html)** — the click-to-copy install walkthrough plus your first ten minutes with the loop. **Never used Claude Code before?** Start one step earlier with **[`INSTALL-CLAUDE-CODE.html`](docs/INSTALL-CLAUDE-CODE.html)** — it installs Claude Code itself, then hands off to `start.html`.

## The problem

Every new Claude Code session starts cold. You re-paste the project at the top of each chat. You hit the context limit mid-task and lose where things stood. You approve the same safe actions over and over, then watch the same mistake recur because the fix never got written down. And the handoff a previous session *did* leave you? You trust it on faith — until you find it was already half-stale.

The single largest cost of serious work isn't the reasoning — it's the **re-introduction**, and the **drift** that creeps in across the gap. Svaha closes both with a single loop instead of a pile of separate features.

## The loop

The whole system is one closed circuit. Each pass leaves the next one a little better calibrated:

1. **Decide with conviction.** A recommendation carries how sure it is and the real tradeoff — not a flat menu of look-alikes.
2. **Record it in the handoff — with its outcome.** When context fills up (or you just say *"that's it"*), the session writes a frozen, numbered `_NEXT_NNN.md` capturing exactly where things stand, what's next, and the decisions made *with their conviction and what actually happened*. Handoffs are immutable like commits, so history never gets rewritten and nothing live silently vanishes. Run several sessions at once — each gets its own numbered **handoff slot**, so no two clobber each other's file.
3. **Verify at the next boot.** The next session doesn't *trust* the handoff — it reconciles the handoff's *claimed* state against *verified* reality (files, tests, what's actually live) before acting. Finished work that isn't actually finished gets caught here, not three sessions later.
4. **A miss becomes a rule.** A high-conviction call that didn't pan out is a calibration miss. On the second miss of the same kind, it's promoted to a rule that **retunes the gate** — so the next decision of that shape is made more carefully.

Continuity feeds coherence feeds better decisions feeds continuity. That circuit is the product; everything else is a piece of it.

Two more things hold it together:

- **One Risk Gate decides ask-vs-act.** Every action is weighed on three axes at once — **conviction** (is this the right call), **reversibility** (how cheaply it rolls back), and **blast-radius** (how much it touches). Cheap-to-reverse, low-blast, high-conviction → it just acts. Expensive-to-reverse or wide-blast → it stops and confirms, *regardless* of how sure it is. A hard set of **auto-escalations** (money movement, any external-service write, destructive ops, a large diff) force a stop even at top conviction.
- **It blocks the genuinely dangerous, and stays coherent as it grows.** A runtime security guard (`bin/security-guard.py`) denies reads of credential/secret files and catastrophic shell ops (`rm -rf ~`, `curl | sh`), and a version guard hard-blocks edits to frozen handoffs. A coupling map, an edit-time drift-guard, a boot/stop coherence check, and a periodic `/audit` catch the slow rot that creeps into any growing config. It watches its own context budget too — a transcript byte-size signal (~400KB/700KB) nudges a wrap-up, a heads-up not a guarantee, so the explicit *"that's it"* stays the reliable path.

## Core + optional operator layer

`CLAUDE.md` is **modular**, split along the Risk Gate. The **core** is the safety skeleton — the handoff loop, the context budget, and the reversibility/blast-radius half of the gate that stops on every unsafe action. The clearly-fenced **Operator layer** is the *judgment half*: conviction calibration, weigh-before-you-ask ordering, premortem rigor, and the conviction-tracking that drives the calibration loop. Keep it for the full self-tuning experience, delete the block for a lean core that still stops on everything dangerous, or copy just that block onto a `CLAUDE.md` you already have.

It travels, too: `CLAUDE.md` is canonical; [`AGENTS.md`](AGENTS.md) is the vendor-neutral mirror that Codex, Cursor, and other agents read (summarizing the universal core). The hooks, slash commands, and `bin/` scripts stay Claude-Code-specific.

## Install

> **Prefer click-to-copy?** Open **[`start.html`](docs/start.html)** in a browser — the full from-scratch walkthrough with a Copy button on every command; `setup.sh` does the `<kit-dir>` substitution + JSON validation for you.

### Quickest — run the installer

```bash
git clone https://github.com/88k8sh/svaha && cd svaha
./setup.sh
```

`setup.sh` copies the slash commands + hooks into `~/.claude/`, **offers to generate your `settings.json`** (only if you don't already have one, and only with consent — it never clobbers an existing `settings.json` or `CLAUDE.md`), and points you at the optional MCP companions. After it runs, **verify the wiring with `bash bin/doctor.sh`** and start with `/session` (or just **svaha**). The snippet ships a **safe-by-default permission posture** — reads & inspection run silently, `git push` / `gh` / `rm` / network / secret-reads always confirm or hard-deny, and **editing is your pick:** Mode A grants edit permission once at install (silent edits, ships as default), Mode B asks once per session (delete three lines). The header comment spells out both.

### Track A — just the behavior (~1 minute)

```bash
cp CLAUDE.md ~/.claude/CLAUDE.md      # global, every project
# or
cp CLAUDE.md ./CLAUDE.md              # scoped to one repo
```

### Track B — the full self-calibrating loop

The verified handoff and `/session` need two halves: the **machinery** (slash commands, hooks, `bin/` scripts) installed once into `~/.claude/`, and a **per-project data layer** (`next/`, `ledger/`, `memory/`, `_LOADUP.md`, `_ARCHIVE/`) in each project the loop should carry.

```bash
# 1. install the machinery + wire settings.json (once)
./setup.sh

# 2. in each project you want the loop, scaffold its data layer
cd ~/your-project
claude            # then run:  /init
```

`setup.sh` installs the seven slash commands and six hooks and wires `settings.json` (filling in the kit's absolute `<kit-dir>` path, validating the JSON, or safe-merging into an existing config). `/init` then turns the current directory into a bootable `<system-dir>` — it creates the data folders and seeds a fresh `CHANGELOG`, but never copies the machinery (that stays in the kit). Fill in the `_LOADUP.md` placeholders it leaves, then `/session` boots the loop.

The completeness spec in `CLAUDE.md` lists all five layers. A `.claude-plugin/plugin.json` also ships, so Svaha can be installed through the Claude Code plugin system.

## What's in the box

A complete package is five layers — missing any one produces a system that runs but doesn't hold coherence over time.

| Layer | Files |
|---|---|
| **1 · Handoff loop** | `_NEXT.md`, `_LOADUP.md`, `boot.md`, `session.md`, `handoff.md`, `reflect.md`, `foldin.md`, `bin/next-write.sh`, `bin/next-live.sh`, `next/` |
| **2 · Guardrail shell** | `bin/drift-guard.py`, `bin/security-guard.py`, `bin/version-guard.py`, `bin/coherence-check.py`, `audit.md`, `SYNC_MAP.md`, `SYSTEM_MAP.md` |
| **3 · Canary hooks** | `hooks/context-canary.sh`, `hooks/launchpad-nudge.sh`, `hooks/memory-reflect.sh`, `hooks/resume-line-guard.sh`, `hooks/session-end-backstop.sh`, `hooks/session-start-marker.sh`, `settings.json.snippet` |
| **4 · Memory** | `memory/MEMORY.md` index + per-entry files |
| **5 · Ledger** | `ledger/` — `CHANGELOG.md`, `DECISIONS.md`, `LESSONS.md`, `session-fixes.md`, `USER_TASKS.md`, `audit-state.md` · plus `_ARCHIVE/` at the system root |

## Composes with your stack

Svaha is the cross-session **spine** — it doesn't reimplement the ecosystem, it composes with it: pair it with **Superpowers** (engineering-skill methodology), **Context7** (live library docs via MCP), or **TLDR-code** (semantic code comprehension over a big repo). Community *patterns* (frozen-artifact enforcement, resume-with-verification, premortem framing, 2-strike correction promotion) are already folded in — nothing to install. Full acknowledgments in [CREDITS.md](docs/CREDITS.md).

## Privacy & provenance

Svaha is a **de-identified extraction** of a real personal Claude Code system that's been running daily for months — which is why the rules read like they were earned (they were). It ships **zero personal data**: every example uses generic `<kit-dir>` / `<system-dir>` / `<Project Name>` placeholders. The dated incidents in `CLAUDE.md` (a lost file, a stranded handoff, a degraded dashboard) are real catches from the origin system, kept because the concrete failure is what gives each rule its teeth.

## License

[MIT](LICENSE) — free for any use. If it saves you the re-introduction tax even once, it did its job.
