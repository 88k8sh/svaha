# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

---

## 2026-06-23 — Svaha rebrand: repo/folder rename (the deferred step) + package as current best

Completed the **repo/folder rename** that the 2026-06-22 content-sweep entry deliberately deferred. Decision (Aakash, this session): the original full Throughline is redundant — **ship the Core as Svaha** as the current best version. Public brand **Svaha**; distilled product keeps the `-core` distribution semantic.
- **Folder renamed:** `~/Claude/throughline-core` → `~/Claude/svaha-core` (git intact from the new path; nothing executable referenced the old absolute path — the live aakash_os hooks point at `aakash_os/`, not this kit).
- **Lowercase `throughline` swept** (the refs the prior entry left untouched): clone URLs + `cd` target in `README.md` and `INSTALL.html` → `svaha`; the `~/throughline` permanent-folder hint + two "throughline folder" prose refs in `INSTALL.html` → `svaha`; `.claude-plugin/plugin.json` name + homepage + repository → `svaha` / `github.com/88k8sh/svaha`; `portrait/README.md` `throughline/portrait/` → `svaha/portrait/`.
- **`LICENSE`** — "Throughline contributors" → "**Svaha** contributors" (the legal line the prior entry explicitly held "until the deliberate repo-rename pass" — this is that pass).
- **Kept intentionally:** the common-noun "throughlines of the becoming" in `portrait/portrait.md`; frozen history (this CHANGELOG, `DISTILLATION-LOG.md`); `_ARCHIVE/`; `<system-dir>` install-time placeholders (not the literal brand).
- Verification: case-insensitive `throughline` grep across active files returns only the intentional keeps above. Committed locally as a reviewable snapshot + rollback point.
- **Deferred to an external-confirmation beat (not done this turn):** (1) GitHub repo rename `88k8sh/throughline` → `svaha` + reconnecting a remote + publishing — the **public repo holds the OLD pre-rebrand full kit (pushed Jun 21) and shares no git ancestry** with this local Core (first commit Jun 22), so publishing = force-push over unrelated history → archive-first + explicit go required. (2) `THROUGHLINE-SAFETY-CHARTER.md` (lives at `~/Claude/` root, outside this tree, referenced by `MANIFEST.md`) → `SVAHA-SAFETY-CHARTER.md` — non-git path, needs archive-first.

## 2026-06-23 — INSTALL-CLAUDE-CODE.html: pre-install / first-time guide

Added `INSTALL-CLAUDE-CODE.html` (top-level) — the missing pre-step for people who have **never used Claude Code (or the Terminal) before**. Fills the gap `INSTALL.html` §0 named but didn't cover ("install Claude Code first"). macOS-primary, same click-to-copy style + copy-button JS as `INSTALL.html`. Steps: open Terminal (Spotlight) → native installer `curl -fsSL https://claude.ai/install.sh | bash` → `claude --version` → `claude` login (browser) → `claude doctor` → `xcode-select --install` for git+python3 so every `INSTALL.html` §0 prerequisite comes up green. Compact Windows/Linux pointer box + troubleshooting table. Install commands **verified against Anthropic's live docs** (code.claude.com/docs/en/setup + /quickstart) — native installer is recommended (self-contained, no Node.js needed); states the **paid-plan requirement** (free plan has no Claude Code access). New onboarding chain: **INSTALL-CLAUDE-CODE → INSTALL → WELCOME**. Cross-links wired: `INSTALL.html` §0 note + expect line, `WELCOME.html` lede, `README.md` "New here?" line. `INSTALL.html` archived → `_ARCHIVE/INSTALL.html.2026-06-23.prebak`. Generic/de-identified — ships with the kit.

## 2026-06-22 — Svaha rebrand: content rename sweep (Throughline → Svaha)

Completed the **rename sweep** the entry below flagged as pending. Capital `Throughline` → **Svaha** across 14 active files (README, INSTALL.html, WELCOME.html, setup.sh, bin/doctor.sh, MANIFEST.md, CREDITS.md, portrait/*). **Content only — repo/folder rename deliberately deferred:** every lowercase `throughline` (paths, the `throughline-core` dir, the GitHub URL, `<system-dir>` refs) left untouched (13 refs, count unchanged) so nothing breaks. **Skipped:** `LICENSE` (legal — "Throughline contributors" stays until the deliberate repo-rename pass), `CHANGELOG.md` + `DISTILLATION-LOG.md` (frozen history), `_ARCHIVE/`. Casing decision: **Svaha** (title-case). Self-caught + reverted one leak — a slash-anchored skip pattern (`/LICENSE$`) missed the top-level LICENSE (grep emitted it with no `./` prefix) and swept it; the git diff-review caught it, reverted clean. Website rebrand (`context-system-site`) still pending — separate Opus/high build.

## 2026-06-22 — Svaha: the assent word, wired into the contract

Added the **svaha** assent token to `CLAUDE.md` (Operator layer, right after "Don't manufacture optionality" — i.e. where "one word from doing it" lives): accept **svaha** / **स्वाहा** / "so be it" / "make it so" / "go ahead" (+ voice mis-hearings *swaha*, *sva ha*) as the affirmative → proceed, no further confirmation; and seal a completed `/handoff` on the same word. The system is being **rebranded Throughline → Svaha** — the name and the assent ritual are now one (rename sweep + website pending). Optional flavor (lives in the Operator layer, deletes with it). Voice-robust by design — it accepts the meaning "so be it," so dictation wobble never breaks it. Anti-overuse + Devanagari refinement: the assistant says it back **only at a true seal** (a `/handoff` completing), at most once, never as filler or mid-turn, rendered स्वाहा. Framed as a **grace note, not the pitch**; **any** clear affirmative proceeds (svaha is the *named, optional* form, not a requirement); the स्वाहा seal doubles as a receipt-of-understanding for garbled dictation; modeled, never pushed. Prior `CLAUDE.md` archived → `_ARCHIVE/CLAUDE.md.2026-06-22.prebak`.

## 2026-06-22 — Install UX: setup.sh settings generator, bin/doctor.sh, WELCOME.html

Closed the remaining install friction:
- **setup.sh** now offers to **generate `settings.json`** (Step 4) — strips the snippet's `//` header, substitutes `<system-dir>` with the kit root, validates the JSON, writes it behind a y/N prompt. Never clobbers an existing `settings.json` (writes `settings.generated.json` to merge instead). Header + SAFETY-CONTRACT updated; prior `setup.sh` archived → `_ARCHIVE/setup.sh.2026-06-22.prebak`. Verified end-to-end in a sandbox HOME.
- **bin/doctor.sh** (new) — post-install check: commands, hooks, kit `bin/` scripts, `settings.json` valid + no leftover `<system-dir>` + hooks wired + the wired guard path actually exists. ✓/✗ with fix hints, exit 0/1.
- **WELCOME.html** (new) — onboarding / how-it-works guide: the loop, the features, the slash commands, a first-ten-minutes walkthrough, where things live.
- SYNC_MAP coupling added (snippet format ↔ setup.sh / INSTALL.html / doctor.sh). README points at all of it.

## 2026-06-22 — Click-to-copy INSTALL.html

Added `INSTALL.html` (top-level) — a from-scratch, copy-button install walkthrough. Step 3A bakes the `<system-dir>` substitution + JSON validation into one paste (`sed`-strip-comments → fill path → write → `json.tool` check), turning the fiddly manual `settings.json` merge into a single command for users with no existing config (the manual-merge path is documented too). Verified: produces valid JSON with 0 leftover placeholders. README points at it. Generic/de-identified — ships with the kit.

## 2026-06-22 — Safe-by-default permissions posture (selectable edit mode) in settings.json.snippet

Added a `permissions` block so a fresh install isn't a per-action flood, with a user-pickable edit mode:
- **allow** (31) — SILENT: file reads, inspection bash, read-only git, the kit's own `bin/` plumbing — plus **file edits** in the shipped default. **Edit Mode A** (ships as default): `Edit`/`Write`/`MultiEdit` in `allow` = one grant at install, never re-asks. **Edit Mode B**: delete those three lines = asks once per session (press "2"). Push/delete/secrets gated either way.
- **ask** (7) — confirm every time: `git push`, `gh`, `rm`, `curl`/`wget`, `git reset --hard`.
- **deny** (14) — secret reads (`.env`/`.pem`/`.ssh`/keys), `rm -rf`, `sudo`, pipe-to-shell.

Precedence **deny > ask > allow** (the ask/deny floor catches a risky "allow always" too). Guard hooks untouched — version-guard still hard-blocks frozen-file edits. Prior snippet archived → `_ARCHIVE/settings.json.snippet.2026-06-22.prebak`. SYNC_MAP coupling row added (permissions ↔ security-guard floor).

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
