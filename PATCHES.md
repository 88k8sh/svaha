# Svaha — Patch Notes

Changes to the Svaha base rules (CLAUDE.md) and firmware files by version.

**To update:** `cd svaha-core && git pull && ./setup.sh`

`setup.sh` detects the `<!-- SVAHA:BASE -->` markers in your `~/.claude/CLAUDE.md` and patches only the Svaha-owned block — your customizations below `<!-- SVAHA:BASE:END -->` are never touched. Commands and hooks are already updated on each `./setup.sh` run (they back up before overwriting).

---

## v0.6.2 — 2026-06-26

**Kit-as-`<system-dir>` footgun closed — the kit folder can no longer be booted or written to as a user system.**

The kit shipped a live-layout `_LOADUP.md` + `next/_NEXT_001.md` at its root, so the kit folder itself resolved as a valid `<system-dir>`: a `svaha` / `/handoff` run from inside the kit (e.g. while developing Svaha) would boot the kit's seed loop or mint a `_NEXT` into the shipped repo — with no error. This release makes that structurally impossible.

### What changed

- **MOVED** the seed templates out of live layout — `_LOADUP.md` → `templates/_LOADUP.template.md` (renamed so no file named `_LOADUP.md` exists in the kit: the resolver anchors on that name, and its one-level child down-scan would otherwise re-resolve a `templates/_LOADUP.md`), and `next/_NEXT_001.md` → `templates/_NEXT_001.md`. `next/` removed from the kit; `/init` now copies from `templates/`.
- **NEW `.svaha-kit`** marker at the kit root. `bin/next-write.sh` / `next-boot.sh` / `next-consume.sh` refuse to operate on a dir carrying it; `/init` refuses to scaffold there; `bin/coherence-check.py` runs `KIT_MODE` (verifies `templates/` instead of a root `_LOADUP.md`, so the kit's own `--boot` stays clean).
- **EDIT** resolution prose — `CLAUDE.md` "Two paths" (base block), `commands/session.md`, `commands/boot.md`: a `.svaha-kit` dir is the kit, not a system — refuse and redirect to a real project.
- Supporting coherence: `MANIFEST.md`, `SYSTEM_MAP.md`, `SYNC_MAP.md`, `FIRST_USER_READINESS.md`, `README.md`.

### Upgrading from v0.6.1

Run `git pull && ./setup.sh` — it re-copies the firmware commands and `bin/`. **Existing user projects are unaffected** (their `_LOADUP.md` is untouched; only the kit's own layout changed). **Manual patch:** in your kit, move root `_LOADUP.md` → `templates/_LOADUP.template.md` and `next/_NEXT_001.md` → `templates/_NEXT_001.md`, point `commands/init.md`'s copy-sources at `templates/`, add an empty `.svaha-kit` file at the kit root, and copy the updated `bin/next-write.sh` / `next-boot.sh` / `next-consume.sh` / `coherence-check.py`.

---

## v0.6.1 — 2026-06-26

**`setup.sh` end-of-run banner — the two silent-failure modes can no longer scroll past unseen.**

Two install conditions silently cripple Svaha: a missing `jq` makes the six shell hooks no-op, and a space in the kit path makes the four Python guards word-split and silently disable. Both were already warned about inline during Step 1 — but those warnings scroll off-screen during the 6-step install, so a user who looks only at the final screen never sees them.

### What changed

- **EDIT `setup.sh`** — the early checks now set `JQ_MISSING` / `SPACE_IN_PATH` flags, and Step 6/6 re-surfaces a consolidated `⚠ INSTALL INCOMPLETE / DEGRADED` banner at the very end (where the user is actually looking) whenever either fired, with the exact fix command. Purely additive — the inline Step-1 warnings are unchanged; no behavior changes when both conditions are clean.

### Upgrading from v0.6.0

Run `git pull && ./setup.sh`. No action needed beyond re-running — the new banner only appears if your install is missing `jq` or sits at a path with a space. **Manual patch:** copy the updated `setup.sh` from this repo.

---

## v0.6.0 — 2026-06-25

**Out-of-tree supersession registry — the boot sweep can now see completions made outside this tree.**

A `_NEXT` move finished *outside* your system root (a published package, an essay, a sibling repo) writes no in-tree completion signal — no `(_NEXT_NNN)` CHANGELOG marker, no `.consumed`, no commit — so its slot reads live forever and can re-mint into a fresh slot that defeats every staleness gate. This release adds the missing channel.

### What changed

- **NEW `bin/external-done.sh`** — single-writer for the registry; append-only, idempotent, pipe-guarded, root-guarded on `<system-dir>/_NEXT.md`, bash-3.2-safe. Records a `predecessor → superseder` supersession the completing session has adjudicated; never decides liveness, never retires a slot.
- **NEW `ledger/EXTERNAL_DELIVERABLES.md`** — the append-only registry (ships with header + schema + illustrative examples). `/init` scaffolds it into a fresh project; existing projects get it auto-created on first `external-done.sh` call.
- **EDIT `commands/boot.md`** — Step B is now **registry-FIRST**: it greps the registry before any `reads:`-hint inference (and not behind the git checkpoint diff, since out-of-tree work commits nothing), adds a fifth classify value `superseded`, and demotes inference to a silent-registry fallback gated on the two-signal archived-source-AND-live-superseder rule so it won't false-fire on `_ARCHIVE/` namesakes. The sweep classifies/warns only — it never auto-retires.
- **EDIT `commands/session.md`** — one-line registry-first pointer in its Step-4b Step-B bullet (boot.md stays canonical; not restated).
- **EDIT `commands/handoff.md`** — the Supersede-stamp step now records out-of-tree completions via `external-done.sh`.
- **EDIT `commands/init.md`** — scaffolds the registry seed into new projects.
- Supporting coherence: `VERSION`, `MANIFEST.md`, `SYNC_MAP.md`, `_LOADUP.md §3`/`§7`, `CLAUDE.md` (content-placement + completeness spec), `bin/drift-guard.py` (boot-loop pattern), `bin/doctor.sh` (must-have list), `ledger/CHANGELOG.md`, `ledger/DECISIONS.md`.

### Upgrading from v0.5.0

Run `git pull && ./setup.sh` — it re-copies the firmware commands and `bin/external-done.sh`. New projects get the registry seed from `/init`; existing projects auto-create `<system-dir>/ledger/EXTERNAL_DELIVERABLES.md` the first time `external-done.sh` runs (no manual step; the seed file is never clobbered — append-only). **Manual patch:** copy `bin/external-done.sh` into your kit `bin/`, copy `ledger/EXTERNAL_DELIVERABLES.md` into `<system-dir>/ledger/` (or let the script create it), and apply the `boot.md` Step-B registry-first edit shown above.

---

## v0.5.0 — 2026-06-25

**Baseline release — versioning and patch infrastructure introduced.**

This is the first versioned release. All prior work merged into this baseline.

### What changed

- **Section markers added to `CLAUDE.md`** — `<!-- SVAHA:BASE:START:v0.5.0 -->` before `## Boot` and `<!-- SVAHA:BASE:END -->` after the final rule. These enable the section-patch path in future `./setup.sh` runs.
- **`VERSION` file** — single-line semantic version; read by `setup.sh` and `bin/doctor.sh`.
- **`setup.sh` — three-path CLAUDE.md logic:**
  - Fresh install → writes kit template as before
  - Markers found → patches only the Svaha base block (new)
  - No markers (legacy install) → offers wholesale replace as before
- **`bin/doctor.sh`** — version check added as check #0.

### Upgrading from a pre-v0.5.0 install

Run `git pull && ./setup.sh`. When prompted about `CLAUDE.md`, answer `y` to overwrite — this adds the markers that unlock automatic section-patching in all future updates. Your existing Svaha rules will be in the marked block; add any project-specific rules below `<!-- SVAHA:BASE:END -->` after.
