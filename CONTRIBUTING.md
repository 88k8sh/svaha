# Contributing to Svaha

## The layer model

Svaha splits into two layers:

**Firmware** (Svaha-owned — patches land here):
- `bin/` scripts
- `commands/*.md` slash commands
- `hooks/*.sh` hooks
- `settings.json.snippet`
- The Svaha base block in `CLAUDE.md` (between `<!-- SVAHA:BASE:START -->` and `<!-- SVAHA:BASE:END -->`)
- `setup.sh`, `bin/doctor.sh`, `VERSION`, `PATCHES.md`

**User-owned** (never touched by patches):
- `CLAUDE.md` below `<!-- SVAHA:BASE:END -->` — your project rules
- `ledger/`, `memory/`, `next/`, `_LOADUP.md`, `_ARCHIVE/` — your project data

## How to submit a fix

1. Fork the repo, create a branch from `main`
2. Make your change — **firmware files only**
3. Test with a fresh install on a clean machine or temp dir: `./setup.sh`
4. Verify: `bash bin/doctor.sh`
5. Open a PR with: what broke, how you reproduced it, what the fix does

**If your fix touches `CLAUDE.md`:** edit only inside the `<!-- SVAHA:BASE:START -->` / `<!-- SVAHA:BASE:END -->` block. Add an entry to `PATCHES.md` and bump `VERSION`.

## What makes a good fix

Good: a hook that silently breaks on Linux, a script edge case, a setup.sh failure mode, a CLAUDE.md rule that produces wrong behavior.

Not a good fit: personal preferences, project-specific additions, things that only make sense for one setup.

## Bash 3.2 rule

All shell scripts must run on macOS `/bin/bash` (3.2.57). No `mapfile`, no associative arrays, no `[[` without single-bracket fallback, no process substitution in contexts that might run under `set -e`. Run `bash -n yourscript.sh` and test on macOS before submitting.
