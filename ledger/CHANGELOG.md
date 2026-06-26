# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

---

## 2026-06-26 — Plugin packaging layer (v0.7.0)

- **NEW** `hooks/hooks.json` — the 10 hooks (6 shell + 4 Python guards) translated into the plugin hook schema, scripts referenced via `${CLAUDE_PLUGIN_ROOT}` (swapped from the `settings.json.snippet`'s baked `<kit-dir>` / `$HOME/.claude/hooks`). Auto-discovered; the one artifact that makes hooks fire under the plugin model. JSON validated; all 10 script paths resolve.
- **NEW** `.claude-plugin/marketplace.json` — single-plugin marketplace, `source: "./"` (the repo root is the plugin). Install identity `/plugin install svaha@svaha`. Plugin `description` states the incompleteness loudly (commands+hooks only; no `CLAUDE.md` contract, no permission floor — `setup.sh` stays canonical).
- **EDIT** `VERSION` 0.6.2→0.7.0; `.claude-plugin/plugin.json` version 0.1.0→0.7.0 (was stale since creation; now the single version source the marketplace entry inherits — marketplace entry omits `version` deliberately so there's one source, not three).
- **EDIT** `PATCHES.md` v0.7.0 entry + manual-apply path; `MANIFEST.md` (two new shipped-file rows); `SYNC_MAP.md` (plugin-layer coupling row).
- **Purely additive** — `setup.sh` never reads either new file, so both install paths coexist; the two files are the smallest safe path from `PLUGIN_PACKAGING_RECON.md` §6. No existing install machinery touched.
- Known limitation deferred: `security-guard.py`/`version-guard.py` log to `__file__`-relative paths (cache dir under the plugin model, wiped on update) — port-time fix is `${CLAUDE_PLUGIN_DATA}`; affects log persistence only, not hook firing.
- Lands on top of `02aeb41` (v0.6.2). Both v0.6.2 and v0.7.0 unpushed at commit time — push is user-gated.

---

## 2026-06-26 — Kit-as-system-dir footgun closed (v0.6.2)

- **MOVED** `_LOADUP.md` → `templates/_LOADUP.template.md`, `next/_NEXT_001.md` → `templates/_NEXT_001.md`; removed `next/` from the kit. The kit root no longer holds a `_LOADUP.md` resolver anchor (renamed so the one-level child down-scan can't re-resolve it either). `commands/init.md` copies from `templates/`
- **NEW** `.svaha-kit` marker — `bin/next-write.sh` / `next-boot.sh` / `next-consume.sh` refuse a marked dir; `commands/init.md` Guard 0 refuses to scaffold there; `bin/coherence-check.py` `KIT_MODE` verifies `templates/` not a root `_LOADUP.md`
- **EDIT** `CLAUDE.md` "Two paths" (base block) + `commands/session.md` + `commands/boot.md` — a `.svaha-kit` dir is the kit, not a system: refuse + redirect
- **EDIT** `VERSION` 0.6.1→0.6.2; `PATCHES.md` v0.6.2 entry + manual-apply path
- **EDIT** `MANIFEST.md`, `SYSTEM_MAP.md`, `SYNC_MAP.md` (§4 anchor caveat + new kit-guard coupling row), `FIRST_USER_READINESS.md` (§3 now mechanically enforced), `README.md`
- `bin/drift-guard.py` + the two Stop/SessionEnd hooks intentionally NOT edited — after the relocation they no longer resolve the kit, so they no-op naturally
- Lands on top of concurrent `ce4925c` (setup.sh banner, v0.6.1) and `fc67af2` (plugin recon); neither file touched by this branch

---

## 2026-06-26 — setup.sh end-of-run install-health banner (v0.6.1)

- **EDIT** `setup.sh` — Step 1 checks now set `JQ_MISSING` / `SPACE_IN_PATH` flags; Step 6/6 re-surfaces a consolidated `⚠ INSTALL INCOMPLETE / DEGRADED` banner at end-of-run (with the fix command) whenever either fired, so the two silent-failure modes (jq missing → 6 shell hooks no-op; space in path → 4 Python guards silently disabled) can't scroll past unseen. Purely additive — inline Step-1 warnings unchanged
- **EDIT** `VERSION` 0.6.0→0.6.1; `PATCHES.md` v0.6.1 entry + manual-apply path

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
