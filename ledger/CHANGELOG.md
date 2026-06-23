# CHANGELOG — Master System Log

Append-only. Newest entries first. One `## YYYY-MM-DD` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by `/handoff` (or manually after structural edits). Do not edit existing entries.

---

## 2026-06-23 — First-handoff teaching note for the स्वाहा seal (one-time)

`handoff.md` now emits a single one-time gloss the *first* time a system seals — detected when `next/` holds only the seed `_NEXT_001` plus the just-written `_NEXT`. An italic line sits between the bottom line and the seal-banner, explaining स्वाहा = the receipt that this session's work is recorded; omitted on every later handoff (the seal stands alone thereafter). This is the *earned* placement of the "say svaha, the system answers in the sacred tongue" moment — at the first real close, never on a cold open (which would be a false seal, against the seal discipline).

## 2026-06-23 — `amen` accepted as an assent word (single seal kept)

`amen` — the cross-tradition twin of *svaha* (both mean "so be it") — joins the accepted affirmatives in `CLAUDE.md`'s assent-word section, alongside the existing yes / go / so be it / make it so. It is an **input only**: however you say yes, the reply stays the one seal, **स्वाहा** — never an echo of your word. A subtle hint was added to `WELCOME.html`'s "One word runs it" box. No custom-anchor *mechanism* was built — the existing "any clear affirmative proceeds" rule already lets your own word work, with no config surface to maintain.

## 2026-06-23 — Agni identity layer pulled from the release (→ separate product)

The optional identity layer (the `portrait/` module, renamed `agni/` earlier the same session) is **extracted from the kit** and set aside as the seed of a separate product — it needs more development than a bolt-on slot in the core release can carry. The released kit ships **without** it: handoff loop, guard shell, hooks, memory, ledger only.

- **Removed from the release, not deleted.** The `agni/` folder (15 files — `agni.md`, `fire.md`, `mirror.md`, `recall.md`, `recall/`, `identity/*.template.md`, the `.gitignore` privacy fence) moved out intact to `~/Claude/agni/` as the product seed. The earlier-staged `portrait/`→`agni/` rename never ships; vs. the published repo this is a clean removal of `portrait/`.
- **References stripped.** README §Agni section, the website identity-layer card + its TOC entry (`docs/index.html`), the SYNC_MAP §3 agni-module row, and the MANIFEST bolt-on row removed.
- **Kept.** Frozen committed CHANGELOG / DISTILLATION-LOG entries that mention `portrait/` stay (history is frozen). (`docs/essay.md`, the old founding-essay, was separately removed as stale this session — author's call.)
- **Net.** The public kit is the pure context-OS again; agni becomes its own product when it's ready.

## 2026-06-23 — Reflection-banner added to the downgrade close

A handoff that downgrades to a reflection now ends with `# ◇ ◇ ◇` (grand hollow), framed by `---` — the distinct sibling of the `# स्वाहा` seal, marking a reflection close (no `_NEXT`, no seal) as opposed to a full sealed handoff. Hollow = nothing carried forward; the pair reads at a glance which close happened. Edited `handoff.md` (downgrade path) + `reflect.md` (standalone not-warranted close). Mirrors the upstream live contract.

## 2026-06-23 — Seal-banner in handoff.md + hero lockup + "ritual" named on the landing site

Three brand/voice fixes to the shippable package:
- **`handoff.md` step 6 — seal-banner.** The close template carried only the bare `Next session:` closer with no seal. Brought it up to the upstream reference (`~/.claude/commands/handoff.md`): the close now ends with the **seal-banner** — `# स्वाहा` framed by a `---` rule above and below — preceded by the bottom line, in the kit's plain `Bottom line:` format. Added the matching prose (seal sits at the foot of the turn, clear of the `Next session:` line `resume-line-guard.sh` reads). Prior version archived → `_ARCHIVE/handoff.md.2026-06-23`. (Direction: upstream `~/.claude` → downstream kit.)
- **Hero lockup — "· so be it" restored.** `WELCOME.html` (`स्वाहा svaha`) and `INSTALL.html` (`स्वाहा svaha — Install`) were missing the third part of the brand lockup that `index.html` carries. Both heroes now read `स्वाहा svaha · so be it` (tagline as a small italic faint span, matching index's `.tag`); INSTALL's redundant `— Install` dropped (the kicker + topbar already say "install"). `INSTALL-CLAUDE-CODE.html` untouched — its hero is the task title "Get Claude Code", not the brand lockup. Verified in-browser (dark mode). Public push to github.com/88k8sh/svaha stays the user's go.
- **"Ritual" named in the `index.html` bookend.** The closing bookend already evoked a ritual (the offering into the fire, a single breath) without naming it; named it once, precisely where the structure lives — `One word turns the loop — three beats of the same word, a small ritual.` with *open* / *confirm* / *close* set in italic so the three beats read as the rite. Deliberately a single use (not echoed in the hero or the "It's one word" card) — the word keeps its weight by being precise, same discipline as the स्वाहा seal. Register-checked: kept out of the essay + data sections, which run on a technical voice. Verified in-browser.

## 2026-06-23 — svaha as the FULL bookend: wired as the close trigger + guides reframed keyword-first

Completed the keyword-replaces-command north star (the prior entry wired only the *opening* half). **svaha** now drives the whole loop:
- **`CLAUDE.md` "## Boot":** the svaha bullet rewritten to a **three-way position rule (priority order)** — (1) first message, nothing loaded → **open** (`/session list`); (2) right after a specific proposal → **assent**; (3) work done / nothing pending → **close** (`/handoff`, same path as "that's it"; Warrant gate decides mint-vs-downgrade). The slash commands stay the explicit equivalents.
- **Auto-handoff HARD RULE:** added **svaha** (said as a *close*, per the position rule) to trigger list (b) alongside "that's it".
- **"Svaha — the assent word" (Operator):** updated so the user's closing svaha is **input** (open/assent/close) and the **स्वाहा seal stays the assistant's output**, firing once when the handoff actually completes. Bright line unchanged.
- **`handoff.md`:** symmetric alias reverse-pointer added (mirrors `session.md`'s svaha-boot pointer). **No new slash command** — svaha maps to existing `/session` + `/handoff`, so the boot-trigger↔command-file coupling (SYNC_MAP §3/§6) holds; drift-guard reconciled.
- **Guides reframed keyword-first:** `WELCOME.html` — new **"One word runs it"** section (the 3 uses + a note explaining the seal स्वाहा is the assistant's *reply*, not your input), commands table demoted to "The explicit commands", first-ten-minutes steps lead with svaha. `INSTALL.html` Step 4 — boot keyword-first + a one-line "svaha to begin, svaha to wrap, seals with स्वाहा" loop note. `INSTALL-CLAUDE-CODE.html` untouched (pre-install, no boot content).
- **Scope:** the shippable package only. Porting the svaha-close to the live `aakash_os` contract is a separate follow-on (not done here).

## 2026-06-23 — "svaha" as a boot trigger (the opening bookend)

Wired **"svaha"** (said as the opening word of a session) as an alias for `/session list` — "make it so / begin." It opens the launchpad; the **स्वाहा** seal still closes a `/handoff`. So svaha now **bookends the loop**: the user *opens* with it (input), the assistant *closes* a handoff with it (output) — same word, opposite directions, no collision (one is input, one is output; the seal's bright-line constraint binds only the assistant's output).
- **EDIT** `CLAUDE.md` "## Boot" — added the svaha boot bullet (→ `/session list`) with the **position-based disambiguation** rule (first message → show the list; mid-session after a proposal → plain assent) and the no-echo-seal guard; added a reciprocal clause in "Svaha — the assent word" clarifying input-vs-output so the seal bright-line isn't misread as forbidding the user's boot use.
- **EDIT** `session.md` — alias reverse pointer (satisfies SYNC_MAP §3's "every `CLAUDE.md` boot trigger must resolve to a real command file"; `/session` already exists, so no new-command registration).
- **EDIT** `WELCOME.html` (commands table + first-ten-minutes step 1), `README.md` (install "start with…") — surfaced the alias where boot is already taught, so users discover it.
- **Website:** deliberately **not** touched — the live site (`bin/context-system-site`) is the conceptual essay, names no commands, and isn't Svaha-branded yet; the svaha-boot/seal bookend belongs in the pending Svaha website rebuild as a unit, not bolted on as the page's only command.

## 2026-06-23 — Onboarding HTMLs reskinned to the website brand

Restyled the three package guides — `INSTALL-CLAUDE-CODE.html`, `INSTALL.html`, `WELCOME.html` — to match the **website's** (`context-system-site`, now at `~/Claude/bin/context-system-site/`) visual identity: warm cream paper (`#FBFAF6`) / terracotta accent (`#B0562A`), Fraunces (headings/wordmark) + Newsreader (body) serif, the two-offset-rectangles continuity glyph in a sticky brand bar, and the site's **full light/dark theme system** (defaults to system preference, toggle in the bar) ported verbatim from the site's CSS variables. Replaced the old cool grey-blue / system-sans GitHub-doc look. WELCOME's navy gradient hero → editorial cream hero (kicker + Fraunces title); loop nodes → pillar cards; feature `.k` tags → accent-soft pills. Command/terminal blocks stay dark in both themes (warm `--term-bg`) with an amber Copy button. **Deliberate departure from the "force `color-scheme: light only`" rendered-artifact rule:** these now ship dual-theme to match the site (which is itself theme-aware and defaults to dark) — safe because dark is *explicitly* themed (not left to invert), which satisfies the rule's intent. Fonts load via Google Fonts (offline → graceful serif fallback). Verified in-browser: both themes render faithfully (screenshots). Prior versions archived → `_ARCHIVE/*.2026-06-23.prerestyle`.

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
