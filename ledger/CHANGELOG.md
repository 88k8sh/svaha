# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

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
