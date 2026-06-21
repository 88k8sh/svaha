# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

---

## 2026-06-22 — Throughline Core: distilled, source-vetted build

Distilled from the full Throughline kit into a concise, afternoon-readable, charter-clean Core.

- **CUT** `bin/context-pct.sh` + the `statusLine` measured-% bridge — the canary's byte-size fallback covers context-fill warning with zero dependency; the measured-% layer was a precision bolt-on (input-token-based, known accuracy limits) the charter named as a prime cut. Canary hooks + `CLAUDE.md` gauge + `SYNC_MAP` now run byte-size only.
- **CUT** `hooks/premortem-suggest.sh` — advisory-only hook that re-raised a rule already in `CLAUDE.md`; it guarded nothing, so it was removed from the always-on hook set (the Premortem rule itself stays in the Operator layer).
- **CUT** `docs/index.html`, `docs/compare.html` — marketing landing pages; not part of the runnable Core (belong on a separate published-site branch).
- **EDIT** `bin/drift-guard.py` — dropped the `drift-guard-fires.jsonl` machine-log subsystem (audit instrumentation, not the prevent layer's job); docstrings compressed. Same firing behavior.
- **EDIT** `bin/coherence-check.py` — removed the `--stop` pre-logging detector (3 helpers); kept boot integrity + plumbing-newer-than-CHANGELOG + audit-delta nudge.
- **SLIM** `CLAUDE.md`, `boot.md`, `handoff.md`, `audit.md`, `SYNC_MAP.md`, `README.md`, `CREDITS.md`, `setup.sh`, `portrait/README.md`, `hooks/context-canary.sh`, `hooks/launchpad-nudge.sh` — removed accretion/duplication; every HARD RULE, guard, and continuity step preserved verbatim. `setup.sh` no longer executes a third-party install or reads an API key (companions are print-only).

---

## Format

```
## YYYY-MM-DD — [session title]
- **NEW** `path/to/file.md` — [what it is and why it was added]
- **EDIT** `path/to/file.md` — [what changed and why]
- **MOVED** `old/path` → `new/path` — [reason]
```
