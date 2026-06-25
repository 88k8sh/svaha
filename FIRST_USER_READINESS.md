# First-User Readiness — Svaha (v0.6.0)

*Assessment ahead of Svaha's first real external user (~3 days out). Scope is deliberately narrow: making the **existing** system understandable and reliable. No new features are proposed. Companion to `ARCHITECTS_GUIDE_TO_SVAHA.md`.*

This was produced from a full read of the kit plus three independent first-user simulations (a Claude Code veteran, a total Claude Code newcomer, and a risk-first architect evaluating adoption). The three personas converged on the same short list — which is the useful signal: the gaps are structural, not persona-specific.

---

## Verdict

**The engine is ready; the on-ramp is not.** The continuity machinery, the guards, and the installer are well-built, defensively coded, and honest about their tradeoffs. The risk is entirely in the **first ten minutes**: the documented happy path dead-ends on the very first action, and two hard dependencies / traps are silent. None of this is a code defect — all of it is a documentation/onboarding gap, and all of it is fixable in well under a day.

If exactly one thing gets fixed before the user arrives, make it **§1 (the `/init` gap)**. If three things, add **§2 (jq)** and **§3 (the kit-as-system-dir trap)**. Those three close every *blocking* or *silent-broken-install* path the simulations found.

conviction: high — all three independent first-user simulations, run blind, surfaced the same `/init` gap as the single blocking defect and the same jq/path traps as the silent ones; the fixes are small and the failures are first-action.

---

## The maturity ledger — what's solid, what's soft, what can wait

The mission asks to separate mature ideas from experimental ones, author's-head assumptions, first-user friction, and debt that can safely wait. Here is that separation in one place.

| Layer | State | Notes |
|---|---|---|
| Continuity substrate (slots, atomic mint, consume, verified handoff, registry) | **Mature** | Defensively coded, race-safe, platform-portable. Ready. |
| Guard layer (security/version/drift/coherence + 6 hooks) | **Mature, but silently dependency-gated** | Solid *if* `jq` + a space-free path are present; otherwise silently degraded (§2, §4). |
| Installer (`setup.sh`, `merge-settings.py`, `doctor.sh`) | **Mature** | Non-destructive, idempotent, safe-merge, JSON-validated, excellent diagnostics. The strongest part of the funnel. |
| First-run onboarding (`start.html` walkthrough) | **Not ready** | The happy path can't succeed as written (§1). This is the gap to close. |
| The calibration loop (conviction → outcome → miss → rule) | **Experimental / aspirational** | The headline feature is the least enforced (see Architect's Guide §15). Fine to ship — but don't over-promise it to the first user as fully automatic. |
| Self-coherence of the shipped docs | **Minor drift present** | Three real inventory/spec inconsistencies (§7). Cosmetic for a user; misleading for a maintainer. Can wait, but cheap to fix. |
| Concurrency under contention | **Advisory by design** | Mint race is closed; shared-content-file races are advisory-only. Fine for single-user; document the boundary (§6). Safe to wait. |

---

## 1. BLOCKING — the first-run walkthrough has no `/init` step

**The single most important finding.** `docs/start.html`'s "Your first ten minutes" walk (the marketed happy path) opens with: *"In a project, start Claude Code and just type `svaha` — it opens the launchpad and resumes where you left off. A brand-new project has nothing to resume yet; that's expected."* (`start.html:246`).

But `svaha` → `/session` resolves `<system-dir>` by finding a `_LOADUP.md`, which **only `/init` creates** (`session.md:11`, `init.md`). On a real fresh project there is no `_LOADUP.md`, so the actual outcome is the message *"the project isn't initialized — run `/init`"* — a command that appears **nowhere in the walkthrough and nowhere in the troubleshooting table** (it's buried once in the reference table, framed as optional: `start.html:281`).

The walk also *conflates two different states*: "initialized-but-empty" (nothing to resume — what the walk promises) and "uninitialized" (run `/init` — what actually happens). They produce different messages and need different fixes.

`README.md` Track B (`:66-79`) *does* state the correct two-step model (install machinery once; `/init` per project). So the correct mental model exists — it just isn't in the walk the user actually follows. **The funnel and the README disagree on whether `/init` is part of first-run.**

**Fix (small):** Add an explicit Step 0 to the walk: *"In your own project, run `/init` once to create the data layer, fill in the `_LOADUP.md` placeholders it leaves, then `svaha`."* Correct the step-1 line so it stops promising "nothing to resume yet" for an uninitialized project.

---

## 2. SILENT-BROKEN-INSTALL — `jq` is an undocumented hard dependency

All six shell hooks parse their stdin with `jq`; **without it they silently no-op** (confirmed `doctor.sh:56-59`, `setup.sh:67-68`). macOS ships no `jq`. Yet:

- `start.html` Step 1's prereq check is `claude --version && python3 --version && git --version` — **no jq** — and the prose says *"It needs `claude`, `python3`, and `git`"* (`start.html:201`).
- `INSTALL-CLAUDE-CODE.html` Step 5 installs `git` + `python3` via `xcode-select` — **no jq** — while framing itself as *"so svaha installs cleanly"* (`:251`).
- `setup.sh` *does* warn (one line, Step 1b), but it scrolls past above the celebratory `स्वाहा` send-off banner and proceeds to report success.

So the default-Mac path is: prereq check passes green → setup "succeeds" → the entire context-canary / launchpad-nudge / memory-reflect / resume-line-guard / session-start-marker / **session-end durability backstop** layer ships **dark, with zero signal.** The user believes the safety net the pitch sells exists; it doesn't. The one thing that catches it is `doctor.sh`, which the walk frames as optional ("Confirm it landed").

**This is the highest-likelihood silent failure for the launch.** The scripts already know `jq` is required — the docs just don't propagate it.

**Fixes (trivial):**
- Add `jq` to `start.html` Step 1's check (`… && jq --version`) and to the stated requirement list.
- Add `brew install jq` to `INSTALL-CLAUDE-CODE.html` Step 5, with one line: *"jq powers the shell hooks."*
- Have `setup.sh` repeat the jq warning *immediately above* the Step 6 send-off banner (where a skimmer will actually see it), not only in Step 1b.

---

## 3. SILENT-WRONG-DIRECTORY — the kit folder is itself a valid `<system-dir>`

Install leaves the user `cd`'d inside the cloned kit (`~/svaha`, per `start.html` Step 2). The kit ships its **own** `_LOADUP.md` at root and `next/_NEXT_001.md`, and `.gitignore` excludes neither — so the **kit folder is a valid `<system-dir>`.** If the user runs `svaha` without `cd`-ing into their own project (the natural next action after `cd svaha`), `<system-dir>` resolves to the kit itself: it boots the kit's seed loop and writes `_NEXT_002` *into the clone*. **No error.** It "works" on the wrong directory.

The walk never says "this folder is the engine — run the loop inside your *own* project, not in here." The architecture's central `<kit-dir>` vs `<system-dir>` split (machinery once, data per-project) is never named anywhere in the funnel, so the user has no model for why "in a project" matters.

**Fix (trivial):** After Step 4, add one line: *"This `svaha` folder is the engine — install it once and leave it here. Run the loop inside your own project folders, not in here."* This both prevents the trap and teaches the kit-dir/system-dir model in plain language at the moment the wrong assumption forms.

---

## 4. SILENT-DEGRADED — a space in the kit path disables all four Python guards

`settings.json` wires the guard commands **unquoted**, so a space in `<kit-dir>` makes the runtime word-split the path and silently disable all four Python guards at runtime — including the security guard (secret-read / `rm -rf` blocking). `setup.sh:72-80` and `doctor.sh:119-121` both go to lengths to catch this; the `-f` file test in `doctor` still passes, so only the *specific* `✗` line reveals it. `start.html` never warns, and its example path (`~/svaha`) is space-free, hiding the hazard. Plausible trip: cloning into `~/Documents/My Stuff/svaha`, a synced "My Drive", or a username with a space.

**Fix (trivial):** One line at `start.html` Step 2 mirroring the scripts: *"Clone to a path with no spaces — a space silently disables the guards."*

---

## 5. DEAD-END — ZIP downloaders hit "permission denied" on `./setup.sh`

`start.html` Step 2 offers a no-git ZIP-download fallback. A ZIP loses the executable bit, so `./setup.sh` fails with `permission denied`. `chmod +x setup.sh` is documented only in `setup.sh`'s own comment, never on the page. A first install command that dead-ends will lose some users.

**Fix (trivial):** Add `chmod +x setup.sh` (or the `bash setup.sh` form) as a fallback note under Step 3's ZIP path.

---

## 6. Assumptions that currently live only in the author's head

These are true and load-bearing but a first-time user (or evaluating architect) cannot derive them from the funnel:

- **Booting is read-only by invariant.** Nothing about resuming mutates durable state except the advisory `.booted` hint. (This is *why* there's no hard lock.) A concurrency-focused evaluator can't find this without reading `next-boot.sh`.
- **There is a human calibrator in the seat.** The "self-calibrating loop" assumes the user watches conviction-vs-outcome over many sessions and decides when to enable auto-act. It is human-in-the-loop, not autonomous. The pitch reads as more automatic than it is.
- **Crash recovery exists but is `jq`-gated and undocumented.** A session that dies without `/handoff` is caught by `session-end-backstop.sh` on SessionEnd/PreCompact — *if* `jq` is installed and the session exits through those events. The strongest reliability story in the system is invisible at the funnel level, so an architect asking "what happens on a crash?" finds no answer and may assume the worst.
- **The ongoing maintenance burden is real but unstated:** apply `SYNC_MAP` couplings + log to CHANGELOG after structural edits; re-run `setup.sh` if you move the kit; fill `_LOADUP` placeholders. An architect's first question — "what do I have to maintain?" — is unanswered on the page trying to convert them.

**Fix (small):** A short "What happens if a session crashes / what you maintain" note in README or `start.html`, naming the backstop (and its jq-gating), the SYNC_MAP+CHANGELOG follow-through, and the move-the-kit re-run rule. The mechanisms exist; surfacing them is pure trust-building at low cost.

---

## 7. Already-present drift in the shipped kit

Real inconsistencies found by an adversarial coherence pass. Cosmetic for a first *user*; actively misleading for a first *maintainer* — and ironically, several are the exact failure classes the kit's own `/audit` is built to catch but cannot run against itself. Good candidates for a new maintainer's first PR (low-risk; teaches the SYNC_MAP discipline).

1. **`MANIFEST.md` buckets a *shipped* file with a *removed* one in its "Cut from Core" list** (`MANIFEST.md:88-92`). The heading reads "Cut from Core (relocated to bolt-on / **published-site tier**)", and `docs/index.html` *does* ship (597 lines; it's the brand-link target of `start.html`) — which is *consistent* with "relocated to published-site tier," not a contradiction. The genuine nit is only that `index.html` (retained) shares one bullet with `docs/compare.html` (genuinely absent), so a reader skimming the cut list may think `index.html` was removed too. *Fix:* split the bullet — `compare.html` cut, `index.html` retained as published-site tier. **(Cosmetic — the weakest of these four; listed for completeness. An earlier draft of this assessment over-rated it as "most serious"; it isn't.)**

2. **The five-layer completeness spec exists in three diverging copies** — `CLAUDE.md` (the self-declared authoritative checklist), `README.md:89`, and `MANIFEST.md:11-26` — and Layer 1 differs across all three. `CLAUDE.md`'s copy *omits* `session.md`, `foldin.md`, `init.md`, `next-live.sh`, `next-boot.sh` (all shipped, all load-bearing — `session.md` is the *primary* boot entry). A maintainer running CLAUDE.md's "is this package complete?" checklist would pass a package missing `session.md`. *Fix:* declare CLAUDE.md canonical, make the others pointers, and bring its Layer 1 up to the shipped set. **(The most consequential of the four — the only one that would actually pass a broken package.)**

3. **`coherence-check.py --boot` checks fewer files than the spec it's coupled to.** `SYNC_MAP §47` claims the `required` list and the completeness spec "must name the same set, or the kit passes while missing a layer" — but `required` (`coherence-check.py:163`) checks 6 data files and omits the hooks, `bin/` scripts, and `SYSTEM_MAP.md`. So `--boot` can report "clean" on a package missing Layer 3. (`doctor.sh` *does* check these, so the *install* path is covered — only the runtime boot check overstates its coverage.) *Fix:* either expand `required`, or soften the SYNC_MAP row to say doctor.sh is the completeness backstop.

4. **Stale cross-reference:** `CLAUDE.md:113` cites "`/audit` Tier-1 check #6 runs `next-live.sh --check`" but `audit.md:39` numbers it **#5** (there is no #6). *Fix:* `#6` → `#5`.

Three smaller ones worth noting but safe to leave: `amen` is documented as an affirmative in `CLAUDE.md` + `start.html` but missing from `AGENTS.md` (mirror lag, arguably within "summary" license); `security-guard.py`/`version-guard.py` write their logs to `<kit-dir>/ledger/` not the project `ledger/` (a deliberate "global machinery" choice, but undocumented — one clarifying docstring line would prevent a maintainer hunting in the wrong place); and `MANIFEST.md` Layer 1 lists `next-write/next-live/next-boot/external-done` but omits `next-consume.sh` (present and load-bearing — `doctor.sh:78` requires it), the same inventory-gap class as items 1–2.

---

## 8. Concepts a competent first-timer won't understand from the docs

Vocabulary used in the funnel without definition (severity rises for the Claude Code newcomer):

- **`<kit-dir>` vs `<system-dir>`** — the architecture's central split; never named in `start.html`. Without it the user can't understand why `/init` exists, why "in a project" matters, or why `svaha` in the kit folder misbehaves (§3).
- **`/init`** — framed as an optional reference command, not the required once-per-project step it is (§1).
- **`jq`** — never named until the doctor fails on it (§2).
- **"launchpad"** — used in `start.html:246` and throughout, never defined for a newcomer (it means `/session list`, the live-slots view).
- **"hook" / "settings.json"** — the newcomer persona is told it copies "6 hooks" and "wires settings.json" with no one-line "a hook is a script Claude runs automatically at certain moments; settings.json is Claude Code's config."
- **The two close-banners (`स्वाहा` vs `◇ ◇ ◇`) and the Warrant gate** — shown on `start.html` with captions, but *why* a wrap sometimes seals and sometimes gives the hollow banner lands before the user has any model of warrant gates, so they read as decorative. A user will wonder why their wrap didn't produce a `_NEXT`.
- **"Verified handoff" / "RESUME-WITH-VERIFICATION"** — the README's headline trust feature, but the funnel never shows what a `claimed: … / verified: …` line looks like, so "can I trust the handoff?" stays an assertion the architect can't validate.
- **"Edit Mode A vs B"** — the snippet/note box use "fenced", "granted once", "per session" without one line: *"this controls whether Claude asks before editing your files."*

**Fix (trivial):** inline parentheticals at first use, plus one sentence introducing the kit-dir/system-dir split (which §3's fix already half-delivers). These remove comprehension cliffs at zero cost to an expert reader.

---

## 9. Implicit onboarding steps (assumed, never stated in the walk)

Consolidated checklist of everything a user must do that the `start.html` walk omits:

1. Install `jq` before relying on the hooks (§2).
2. Clone to a path with **no spaces** (§4).
3. Run `/init` in your actual project before the first `svaha` (§1).
4. `cd` **out** of the kit folder into your real project before booting (§3).
5. Fill in the `_LOADUP.md` placeholders that `/init` leaves (`init.md:90-92`) before the loop is meaningful — a blank `_LOADUP` boots a hollow loop.
6. `chmod +x setup.sh` if you downloaded the ZIP (§5).
7. Actually **run** `bash bin/doctor.sh` and act on any `✗` — it's the only thing that catches the jq / space-path / moved-kit failures, yet the walk frames it as optional.
8. Launch Claude Code from inside your project (so CWD resolution finds the project's `_LOADUP.md`).
9. Re-run `setup.sh` after moving or updating the kit (re-bakes `<kit-dir>` into the installed config).

---

## 10. The punch list — smallest changes, highest leverage

Prioritized for the 3-day window. All are documentation/UX; none touch the loop, guards, or scripts' logic (except optional installer print-ordering).

> **Status (applied 2026-06-26):** items **1–8 are done** in the working tree (`docs/start.html`, `docs/INSTALL-CLAUDE-CODE.html`, `setup.sh` — uncommitted, render-verified). Item **7** edits `setup.sh` (firmware), so a commit should ride a `VERSION` bump + `PATCHES.md`/`CHANGELOG.md` entry. Items **9–11** (glossary parentheticals, crash-recovery note, the §7 shipped-drift fixes) remain open.

| # | Change | Closes | Effort |
|---|---|---|---|
| 1 | Add `/init` (+ fill `_LOADUP`) as Step 0 of the `start.html` walk; fix the "nothing to resume yet" line for fresh projects | §1 (blocking) | small |
| 2 | Add `jq` to `start.html` Step 1 check + prose, and to `INSTALL-CLAUDE-CODE.html` Step 5 (`brew install jq`) | §2 (silent half-dead hooks) | trivial |
| 3 | One line at `start.html` Step 2: "This folder is the engine — run the loop in your own project, not here" | §3 (wrong-directory) | trivial |
| 4 | One line at `start.html` Step 2: "Clone to a path with no spaces — a space silently disables the guards" | §4 (silent guard-kill) | trivial |
| 5 | Reframe `start.html` Step 4 doctor from optional "confirm it landed" to **required** — note the hooks fail silently, so the doctor is the only proof | §2, §4 (the only detector) | trivial |
| 6 | Two troubleshooting rows: "the project isn't initialized — run /init" → run `/init`; "hooks seem dead / no wrap-up nudge" → check `jq`, install, re-run doctor | §1, §2 | trivial |
| 7 | `setup.sh`: repeat any jq / spaced-path warning immediately above the Step 6 send-off banner | §2, §4 | small |
| 8 | `chmod +x setup.sh` fallback note under the ZIP path | §5 | trivial |
| 9 | Inline glossary parentheticals (hook, settings.json, launchpad, init) at first use | §8 | trivial |
| 10 | Short "crash recovery + what you maintain" note in README/start | §6 | small |
| 11 | Fix the shipped-drift items (split the MANIFEST cut-bullet; **canonicalize the completeness spec** — the consequential one; coherence-check coverage note; #6→#5) | §7 | small |

Items 1–8 are the launch-critical set (every blocking and silent-broken-install path). Items 9–11 are quality and maintainer-trust, and can follow the launch if time is short.

---

## What's genuinely solid (to bound the assessment honestly)

So the punch list isn't read as "the system is shaky" — it isn't. These were verified and are ready:

- `setup.sh` / `merge-settings.py` are genuinely robust: non-destructive, idempotent, consent-gated, JSON-validated, safe-merge-with-backup into an existing `settings.json`, and they handle an invalid-JSON existing config gracefully.
- `doctor.sh` is excellent: it checks jq, python3, the 7 commands, 6 hooks, 9 bin scripts, settings validity, leftover `<kit-dir>`, the wired guard path's existence, **and** the space-in-path trap — and names the exact fix per failure. The whole funnel's reliability rests on the user *running* it; the tool itself is complete. (This is why item 5 — making it non-optional — is high-leverage.)
- The continuity machinery, the atomic mint, the verified-handoff boot pass, and the dual-layer secret/destructive-op deny are all sound and defensively coded.
- The `--consume` chain, the out-of-tree registry chain, and the four-way `<system-dir>` resolution algorithm are internally consistent (verified identical across all four implementers).

The gap between this kit and a great first-run is small, specific, and entirely in the documentation. Close items 1–8 and the first user's experience matches the quality of the engine underneath it.
