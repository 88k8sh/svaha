# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

---

## 2026-06-25 — Out-of-tree supersession registry (v0.6.0)

- **NEW** `bin/external-done.sh` — single-writer for the out-of-tree supersession registry; append-only, idempotent, pipe/root-guarded, bash-3.2-safe (ledger/ preferred, 30_LEDGER/ fallback)
- **NEW** `ledger/EXTERNAL_DELIVERABLES.md` — the append-only registry (header + schema + illustrative examples); the missing completion signal for deliverables shipped outside `<system-dir>`
- **EDIT** `commands/boot.md` — Step B made registry-FIRST (grep the registry before `reads:`-hint inference, not behind the git diff; two-signal archive+live-superseder fallback; new classify value `superseded`); Step C + Output block + the do-not-execute gate carry `superseded`. Sweep classifies/warns only — never auto-retires
- **EDIT** `commands/session.md` — one-line registry-first pointer in the Step-4b Step-B bullet (boot.md stays canonical; do-not-restate invariant preserved)
- **EDIT** `commands/handoff.md` — Supersede-stamp step now records out-of-tree completions via `external-done.sh`
- **EDIT** `commands/init.md` — scaffolds the registry seed into new projects (ledger cp loop + report count 8→9)
- **EDIT** `VERSION` 0.5.0→0.6.0; `PATCHES.md` v0.6.0 entry + manual-apply path
- **EDIT** `MANIFEST.md` (Layer-1 `external-done.sh` + Layer-5 `EXTERNAL_DELIVERABLES.md` rows), `SYNC_MAP.md` (§1 registry-contract row + §3 `external-done.sh` coupling row / guard-self reconcile), `_LOADUP.md` §3 map + §7 enum, `CLAUDE.md` (content-placement row + completeness spec Layer 1 + Layer 5), `bin/drift-guard.py` (boot-loop pattern), `bin/doctor.sh` (check4 must-have list)
- **DECISION** `ledger/DECISIONS.md` — boot-sweep-guard hook NOT mirrored (kit Step B is conditional, not a hard-gate mandatory grep; no skip-proof anchor; revisit if a hard-gate grep step is added)
- `bin/coherence-check.py` — intentionally NOT edited (the new script is auto-covered by the PLUMBING_DIRS bin-glob; not a slash command, not a named plumbing file)

---

## 2026-06-25 — Patch management infrastructure (v0.5.0)

- **NEW** `VERSION` — `0.5.0`; read by `setup.sh` and `bin/doctor.sh`
- **NEW** `PATCHES.md` — user-facing changelog for CLAUDE.md base rule + firmware changes; includes manual-apply path for pre-marker installs
- **NEW** `CONTRIBUTING.md` — firmware vs user-owned layer model; PR requirements; bash 3.2 rule
- **EDIT** `CLAUDE.md` — added `<!-- SVAHA:BASE:START:v0.5.0 -->` before `## Boot` and `<!-- SVAHA:BASE:END -->` after final rule; user customizations go below end marker
- **EDIT** `setup.sh` Step 3b — three-path CLAUDE.md logic: (1) fresh install, (2) section-patch when markers found (preserves user customizations), (3) legacy wholesale replace prompt
- **EDIT** `bin/doctor.sh` — version check added as check #0
- **EDIT** `MANIFEST.md` — entries for VERSION, PATCHES.md, CONTRIBUTING.md
- **EDIT** `SYNC_MAP.md` §3 — coupling rows for CLAUDE.md base edits → VERSION + PATCHES.md

<!-- Your first structural change writes the first entry here. -->

---

## Format

```
## YYYY-MM-DD — [session title]
- **NEW** `path/to/file.md` — [what it is and why it was added]
- **EDIT** `path/to/file.md` — [what changed and why]
- **MOVED** `old/path` → `new/path` — [reason]
```
