# Architect's Guide to Svaha

*An onboarding document for the next AI systems architect who will help maintain and evolve Svaha.*

This is not repository documentation. It does not primarily tell you where files live (`SYSTEM_MAP.md` does that, and `MANIFEST.md` is the inventory). It tries to transfer the **mental model** that produced the architecture — the worldview, the bets, the invariants, and the discipline for changing it without breaking what already works.

Read it once, end to end. If at the end you could review a pull request to this repo without asking the original author "wait, why is it like this?" — it did its job.

---

## 0. The one paragraph, and the one lens

**What Svaha is.** A `CLAUDE.md` behavior contract + a small per-project data scaffold (`next/`, `ledger/`, `memory/`, `_LOADUP.md`) + 7 slash-command specs (`boot`, `session`, `handoff`, `reflect`, `audit`, `foldin`, `init`) + 11 `bin/` scripts (the 9 guard/handoff scripts the kit counts in `doctor.sh`, plus the `merge-settings.py` / `doctor.sh` install pair) + 6 hooks, wired through `settings.json`. The thesis is that these are not separate features but **one closed loop**: a decision is made *with its conviction*, frozen into an immutable numbered handoff *with its outcome*, verified against git/grep reality at the next boot, and a repeated high-conviction failure becomes a rule that retunes how the next decision is made. *Continuity feeds coherence feeds better decisions feeds continuity.* That circuit is the product; everything else is a piece of it.

**The one lens you must hold the whole time: claimed vs. enforced.** Most of Svaha is *instruction-level* — the Markdown commands and `CLAUDE.md` *describe* a rigorous procedure the model is asked to follow. Only a thin layer of Python/bash hooks actually *enforces* anything, and that layer is narrow and deterministic. Every time you read a rule, ask: is this **enforced** (a hook denies it, a script makes the failure impossible) or **claimed** (prose the model is trusted to honor, perhaps backstopped by a fail-soft nudge)? This single distinction explains the system's real robustness, where its complexity comes from, and what is safe to change. Keep it lit at all times. The rest of this guide is, in a sense, an elaboration of this one lens.

A corollary you will return to constantly: **the guards catch the model's lapses; they do not make the loop run.** The loop runs because the model follows the contract. The hooks are a thin mesh underneath that catches the highest-cost failures when it doesn't.

---

## 1. The problem Svaha exists to solve

Every Claude Code session starts cold. Models reason fine within a session; the cost was never forgetting *mid-thought*. The tax is everything around the reasoning:

- **Re-introduction.** Each resume, you re-paste the project and hunt for where things stood.
- **The context wall.** You hit the limit mid-task and lose the thread.
- **Repeated approvals.** You approve the same safe actions over and over.
- **Recurring mistakes.** The same error returns because the fix was never written down.
- **Stale handoffs.** The note a prior session left you is trusted on faith — until you find it was already half-wrong.
- **Tangled concurrency.** The moment you run more than one session, their threads collide.

The single largest cost of serious agent work is the **re-introduction**, and the **drift** that creeps in across the gap. Svaha closes both with one loop instead of a pile of separate features. Note the framing carefully: it is not "give the model memory." Memory is the easy half. The hard half — the half Svaha actually attacks — is making cross-session state **trustworthy** and keeping the whole apparatus **coherent as it grows**.

---

## 2. The design philosophy — the load-bearing beliefs

These are the convictions encoded throughout. If you internalize nothing else, internalize these; every concrete mechanism is one of them made real.

1. **A handoff is a claim, not a fact.** The deepest bet in the system. A note written by one session (or one model generation) and read by another is untrustworthy by default. So the next boot does not *trust* the handoff — it *reconciles* the handoff's claimed state against verified reality (git diff + grep + a registry) before acting. Finished-but-not-finished work gets caught at boot, not three sessions later. This single idea is what separates Svaha from a TODO file.

2. **Frozen like commits.** A handoff, once written, is never edited, appended, or merged. A correction is a *new* numbered file. Immutability is what lets one file be simultaneously the operational queue, the audit record, and the verification anchor — and is what makes concurrent writes safe (mint-new, never edit-shared).

3. **Parallel slots, not versions.** The numbered handoffs (`_NEXT_NNN.md`) are a *set of concurrent session slots*, not a linear version history. A higher number is *another session's* handoff, not a newer copy of yours. Concurrency is a first-class design assumption, not an afterthought — the user runs several sessions at once, and the whole plumbing is built to survive that with no database, daemon, or lock.

4. **Conviction and consequence are separate axes.** How *right* a call is (conviction) and how *safe it is to do unasked* (reversibility + blast-radius) are orthogonal. A destructive or irreversible action can be high-conviction and still must stop. Collapsing these into one "confidence" dial is the exact failure the Risk Gate exists to prevent — confidence must never be able to buy down safety.

5. **Mechanisms beat rules.** A rule the model keeps needing reminded of is not under-emphasized — it is in the *wrong form*. There is an explicit conversion ladder: a **judgment rule** (fires only if the model first classifies the moment correctly) → a **phrase tripwire** (fires on a literal token the model is about to emit) → a **hook** (fires regardless of the model's judgment). The heuristic for climbing it: if the same rule is missed twice, change its *form*, not its *volume*.

6. **Local-first, plain files you own.** No database, no daemon, no cloud memory, no lock-in. Everything is plain Markdown and a few scripts in your own repo. When the model gets something wrong, you open the file and fix it — nothing is parked silently where you can't see it. The day a model ships this natively, you delete a folder and walk away. This is also a privacy stance: raw context never leaves the machine automatically.

7. **Fail-open / advisory by default; deny only the catastrophic.** A guard that crashes tools is worse than one that occasionally misses. Every hook fails *open* (any error exits cleanly, never blocking). Only **two** guards ever hard-deny (secret reads + catastrophic shell ops; edits to frozen artifacts). Everything else is an advisory nudge. The system is allow-by-default and acts only on small, high-confidence patterns, so normal work is never touched.

8. **Single source of truth, and do-not-restate.** Each kind of content lives in exactly one canonical place (the content-placement table in `CLAUDE.md`). When two files must describe the same procedure, one is canonical and the other *points* at it — it never restates it — so the two cannot fork. Duplicated content guarantees drift.

9. **Earn your weight (Deletion-First).** `CLAUDE.md` is loaded into *every* session — it is permanent context budget, paid forever by every future session. So an edit to it (or any always-loaded surface) must either cite an offsetting trim or carry a one-line net-add justification. The default is collapse-into-existing, not append-new. The document that holds the rules is itself governed by the rules' spirit.

10. **The system learns from its own track record.** Conviction is not narration — it is a *tracked* signal. A decision is recorded with its conviction and its outcome; the next boot checks the outcome against reality; a high-conviction call that failed is a *calibration miss*; the second miss of a kind promotes a rule that retunes the gate. (Important honesty, see §15: this is the most *aspirational* and least *enforced* layer.)

11. **Real scars, kept as provenance.** Svaha is a de-identified extraction of a personal system that ran daily for months. It ships zero personal data, but the dated incidents in `CLAUDE.md` (a lost file, a stranded handoff, a degraded dashboard) are *real catches*, kept deliberately — because the concrete failure is what gives each rule its teeth. When you read "the failure that stranded `_NEXT_018` on 2026-06-18," read it as "here is what went wrong the day this rule was written." The rules read like they were earned because they were.

---

## 3. The core abstractions — the vocabulary you must hold

To think in Svaha, you need these primitives loaded. Everything in the runtime is composed from them.

- **The slot (`_NEXT_NNN.md`).** A frozen, numbered handoff — a session's final snapshot, treated like a commit. The number is a *slot in a concurrency set*, not a version. Holds a header block + three sections (`## Pending`, `## Next moves`, `## Push to _LOADUP`).

- **Sidecars.** Out-of-band lifecycle state that keeps the slot itself frozen: `_NEXT_NNN.consumed` (the slot is retired), `_NEXT_NNN.booted` (advisory occupancy — a session is likely working it right now). Immutability and live status coexist because status lives *beside* the file, never *in* it.

- **The Verified Handoff header.** The fields that turn a trusted note into a checked contract: `outcome:` (the session's own verdict — `SUCCEEDED` / `PARTIAL_PLUS` / `PARTIAL_MINUS` / `FAILED`), `touched:` (files edited — the clobber-check input), `checkpoint:` (the git SHA the next boot diffs against), `worked:`/`failed:` (strategy memory — lean-on list / do-not-retry list).

- **Read-Map (`reads:`) and Skip-List (`skip:`).** Per-move metadata. `reads:` names the exact files/sections the next session must open before a move — *and* is what the boot pass greps to verify the move is still live. A move with no `reads:` can only ever be classified `unverified`. `skip:` names what's already done so it isn't redone.

- **The five-state classification.** At boot, every open move is classified: `still-true` (work genuinely pending — execute), `already-done` (target already holds the result — do not execute), `stale` (target moved/changed — the move no longer applies), `superseded` (completed/replaced out-of-tree — do not execute), `unverified` (no `reads:` hint or inconclusive — may run, but say so). Only `still-true` auto-executes.

- **The Warrant gate.** The decision at session-end: is a full handoff (and its seal) warranted, or should this downgrade to a reflection? Warranted only by *live carry-forward work* — genuine in-flight work or queued moves *from this session* that would be lost. Context size is explicitly **not** a warrant condition (a big read-only session produces nothing to carry). The "would be lost" test: a state already durably captured in a source file is not a queue item — re-stating it manufactures a phantom queue.

- **The Risk Gate.** The ask-vs-act decision, scored on three axes — conviction × reversibility × blast-radius — with a hard floor of **auto-escalations** (money movement, external-service writes, destructive ops, large diffs) that force a stop *regardless of the score*. (Read "score" as a structured posture, not a numeric formula — see §15.)

- **The svaha word.** One ritual token drives the loop, disambiguated by **position**: first message of a session = *open* (`/session list`); right after a proposal = *assent* (proceed); winding down = *close* (`/handoff`). The Devanagari seal **स्वाहा** is the *reply*, emitted only in a turn where `/handoff` or `/reflect` actually wrote a file — a falsifiable proof-of-commit, never decoration.

- **kit-dir vs system-dir.** The two-path split. `<kit-dir>` is the machinery (`bin/`, hooks, command files) — one fixed location, baked to an absolute path once at install. `<system-dir>` is a project's data (`next/`, `ledger/`, `_LOADUP.md`) — per-project, resolved at runtime by a *bounded* search for `_LOADUP.md` (CWD + ancestors + one level of children, **never recursive**).

- **Firmware vs user-owned.** The upgrade model. Firmware = Svaha-owned files that patches land on (`bin/`, `commands/`, `hooks/`, `settings.json.snippet`, the `CLAUDE.md` block between `<!-- SVAHA:BASE:START -->` / `<!-- SVAHA:BASE:END -->`). User-owned = everything below the end-marker and all project data. `setup.sh` section-patches only the firmware block.

---

## 4. The runtime lifecycle

The loop, concretely:

```
  svaha (open)  →  /session reads the lowest live _NEXT_NNN + _LOADUP
                   → RESUME-WITH-VERIFICATION (verify claims against reality)
                   → status block, then auto-execute the first still-true move
       │
       ▼
   ┌────────┐
   │  work  │   decisions made with conviction; safe acts flow, risky acts stop
   └────────┘
       │
       ▼
  svaha (close) → /handoff
       → Warrant gate: live carry-forward work? 
            no  → downgrade to /reflect (memory + bug log), close with ◇ ◇ ◇
            yes → mint a NEW frozen _NEXT_NNN+1 (atomic), retire the booted slot,
                  log to CHANGELOG, close with the स्वाहा seal
       │
       ▼
  next session boots the _NEXT just minted → loop closes, a little better calibrated
```

**The boot is exactly two files, always:** the named/auto-picked `_NEXT_NNN.md` and `_LOADUP.md`. Everything else is on-demand, pulled via the retrieval index in `_LOADUP §4`. Boot then emits a **proof-of-boot line** (`loaded: _NEXT_NNN ✓ _LOADUP ✓ …`) so drift between "what boot should load" and "what got read" is visible at a glance.

**RESUME-WITH-VERIFICATION (the heart of the boot)** runs four cheap steps — git + grep only, no DB, no agents:
- **Step A — diff against the checkpoint.** `git diff --stat <checkpoint>..HEAD` for the ground truth of what changed since the handoff was written (skipped, grep-only, in a non-git project).
- **Step B — registry-FIRST, then the reads-grep.** First grep `ledger/EXTERNAL_DELIVERABLES.md` for an out-of-tree supersession (this is read *first*, and not behind the git diff, precisely because out-of-tree work commits nothing). Then inspect each move's `reads:` files and classify it.
- **Step C — report, then gate.** One `claimed: … / verified: …` line per move; only `still-true` moves auto-execute.
- **Step D — same-file-clobber check.** Cross-check move 1's intended edits against other live slots' `touched:` lists; warn on overlap, then proceed (advisory).

The sweep *classifies and warns* — it never retires a slot. Retirement stays a human-gated handoff act.

---

## 5. The continuity model — how state survives amnesia

State survives across memoryless sessions through immutable slots and out-of-band sidecars, all in one folder (`next/`), with no archiving sweep.

- **Minting is atomic and collision-safe.** `next-write.sh` computes the next free number, then *reserves* the slot with a `noclobber` O_EXCL create (an atomic test-and-claim) before writing any content — closing the TOCTOU race where two simultaneous mints both passed a `[[ -e ]]` check and one clobbered the other. An EXIT trap drops a zero-byte slot on any crash, so a failed mint never burns a number.

- **Retire rides the mint.** When you booted from a slot, you pass `--consume NNN`; `next-write.sh` writes + checkpoint-stamps the successor, confirms it is non-empty, *then* retires the predecessor via `next-consume.sh`. The two acts are inseparable: you cannot mint a successor while forgetting to retire the predecessor, and the predecessor is never retired before its successor exists. (This is the "consume-leak fix, layer A.")

- **`next-consume.sh` is the single writer of `.consumed`,** idempotent, recording when + why into the sidecar — every retire is one auditable operation. (Layer B. The old hand-typed `touch` was forgettable and unauditable; slots finished *off* the boot→handoff path silently sat falsely-live forever.)

- **`next-live.sh` is the single source of truth for "what is live."** Never eyeball `next/` — it is shared mutable state, and a concurrent `/handoff` consuming a slot mid-listing makes any hand-built list a racy snapshot that silently drops it. The script is deterministic and *race-aware*: it surfaces recently-consumed slots so a session retired by a parallel handoff is shown explicitly, never vanishes. It also flags **DONE-PROBABLE** (a slot the CHANGELOG marks done but that was never stamped — layer C, review-only) and surfaces `.booted` occupancy hints.

- **The out-of-tree supersession registry** (`external-done.sh` + `EXTERNAL_DELIVERABLES.md`) is the missing completion channel. A move finished by shipping something *outside* `<system-dir>` — a published package, a sibling-repo doc, an essay — writes no in-tree signal (no `.consumed`, no CHANGELOG marker, no commit here), so its slot reads live forever and can re-mint into a fresh slot that defeats every staleness gate. The completing session records the supersession; boot.md Step B reads the registry *first*. Recognizing "work that left the tree and left no signal" as a distinct, structurally-invisible failure class — and giving it a dedicated channel — is one of the kit's sharper moves.

- **The `.booted` occupancy hint** is a deliberately *soft* double-booking guard: it warns that a slot is likely in use and lets the no-arg picker skip it, but it is **not a lock**. A hard lock was considered and rejected (see §13) — it would need a stale-lock reaper, break the read-only-boot invariant, and a TTL just re-creates the human "is it really still live?" judgment. The hint needs no reaper because nothing depends on its accuracy.

---

## 6. The state model — where every kind of state lives

The single most important operating rule for a maintainer is **content placement** (the canonical table is in `CLAUDE.md`). Each content type has exactly one home; duplicating across files guarantees drift.

| Kind of state | Lives in | Nature |
|---|---|---|
| Behavior rules / guardrails | `CLAUDE.md` | Always-loaded; the enforcement layer |
| Stable reference facts | `_LOADUP.md §2` | Loaded on boot; "do not re-derive" |
| In-flight work + next moves | `next/_NEXT_NNN.md` | Frozen, per-session |
| Structural changes (the digest) | `ledger/CHANGELOG.md` | Append-only, newest-first |
| Design decisions + alternatives | `ledger/DECISIONS.md` | Append-only; the road not taken |
| Named lessons from incidents | `ledger/LESSONS.md` | Append-only |
| Bugs caught + fixed | `ledger/session-fixes.md` | Append-only |
| Human-only tasks | `ledger/USER_TASKS.md` | The user's lane, not the model's |
| Out-of-tree completions | `ledger/EXTERNAL_DELIVERABLES.md` | Append-only registry |
| Per-session context about the user | `memory/*.md` (indexed by `MEMORY.md`) | "Surprises, not derivable facts" |
| Retired files | `_ARCHIVE/` | No hard deletes |

Two state-model rules deserve emphasis because they are easy to violate:

- **The "Push to `_LOADUP`" valve.** Each `_NEXT` has a `## Push to _LOADUP` section — the channel for a session's settled facts to trickle up into stable reference. It *self-destructs*: the next session that touches `_LOADUP` moves those lines up and deletes the section. This is the one sanctioned path from ephemeral to stable; don't bypass it.

- **Memory holds surprises, not derivable facts.** Store what you *couldn't* reconstruct by reading the code — decisions and why, failures and causes, user preferences. Never store a function signature or file layout; those rot the moment the code moves, and re-reading is cheaper than trusting a stale note. The test: "would a fresh session figure this out by looking?" If yes, don't memorialize it. (This is also why `CLAUDE.md` — not `memory/` — is the home for behavioral corrections: memory is supplementary context, `CLAUDE.md` is the enforcement layer that actually gets followed.)

---

## 7. The behavioral model — the Risk Gate and the calibration loop

Svaha's behavior contract exists because an LLM, left to its in-the-moment gradient, systematically picks the cheap/visible/helpful action over the expensive/deferred/correct one, and over-trusts its own confidence. The behavioral model is the structured counter.

**The Risk Gate** weighs every action on conviction × reversibility × blast-radius, and the result sets *both* ask-vs-act *and* how much scrutiny applies (premortem rigor is scaled to the tier — a cheap reversible action earns a glance; an irreversible one earns a full premortem). Two design facts are load-bearing:

- **Reversibility means a *named* rollback path** — a revert SHA, a feature-flag toggle, an `_ARCHIVE/` copy. Never "I'll just delete the file." If you can't name the rollback, treat it as irreversible. This prevents the model from self-certifying anything as safe.
- **The auto-escalation overrides "do not get a vote."** Money movement, external-service writes, destructive ops, and large diffs force the top tier *regardless* of computed conviction. A scoring system optimized by the same agent it constrains needs a hard floor it cannot reason its way under.

**The Core / Operator split.** `CLAUDE.md` is modular along the gate. The **Core** is the safety skeleton — the handoff loop, the context budget, and the consequence half of the gate that stops on everything unsafe. The clearly-fenced **Operator layer** is the *judgment half* — conviction calibration, weigh-before-you-ask ordering, premortem rigor, the calibration loop. Delete the Operator block and you get a lean core that still stops on everything dangerous; you only lose the self-tuning. The seal hard-guard lives in Core, *not* Operator, deliberately — so deleting the optional block can't remove a correctness property.

**The calibration loop** is the most ambitious idea and the one to understand most carefully:

> decide-with-conviction → recorded-in-handoff-with-outcome → verified-next-boot-against-reality → mismatch is a calibration miss → second miss of a kind promotes a rule → the rule retunes the gate → carried forward.

The `PARTIAL_PLUS` / `PARTIAL_MINUS` outcome split exists precisely so a confidently-planned-but-stalled session is a single greppable token (`grep PARTIAL_MINUS next/`) instead of a flat `PARTIAL` laundering a soft-fail as progress. The schema is designed around the audit query you'll later want to run.

**Dormancy.** The intended payoff — *high conviction + safe action → execute without asking* — is written into the contract but switched **OFF**. Until the user explicitly flips it, conviction is display/track-only and never changes whether the model asks. This is deliberate: the calibration data accrues under the eventual mechanism's exact shape *before* that mechanism gains power, so the user can verify "high" actually tracks reality before trusting it with a skipped confirmation. Read dormancy as "shipped OFF as a safety state," not "TODO." (It is a first-class design artifact: shipping the off-switch on purpose.)

---

## 8. The role of hooks

Hooks are the **enforcement and sensing layer** — the parts that fire *regardless of the model's judgment*. They are wired in `settings.json` and ordered **prevention → entry → exit → periodic** so drift is caught at every stage of a session.

| Stage | Hook | Fires | Does |
|---|---|---|---|
| prevention | `security-guard.py` | PreToolUse (Bash/Edit/Write/MultiEdit/Read) | **DENIES** secret-file reads + catastrophic ops (`rm -rf /` or `~`, `curl \| sh`, fork bomb); **ASKS** on history-/data-losing git (force-push, `reset --hard`, `branch -D`, `clean -fd`) |
| prevention | `version-guard.py` | PreToolUse (Edit/Write/MultiEdit) | **DENIES** edits to frozen artifacts (`_NEXT_NNN.md`, any `frozen: true` file) |
| prevention | `drift-guard.py` | PreToolUse (Edit/Write/MultiEdit) | Injects the relevant SYNC_MAP couplings when a structural file is edited (advisory) |
| entry | `session-start-marker.sh` | SessionStart | Stamps a per-session marker so the durability backstop knows precisely whether a `_NEXT` was written *this session* |
| exit | `context-canary.sh` | PostToolUse | Byte-size context-fill canary (🟡400KB / 🔴700KB), throttled |
| exit | `memory-reflect.sh` | Stop | Tiered nudge to run `/reflect` |
| exit | `launchpad-nudge.sh` | Stop | Heavy-session wrap-up nudge |
| exit | `resume-line-guard.sh` | Stop | Validates the `Next session: /session NNN` closer points at a *live* `_NEXT` |
| exit | `coherence-check.py --stop` | Stop | "Edited X but didn't log it" + audit-due nudge |
| durability | `session-end-backstop.sh` | SessionEnd + PreCompact | If no `_NEXT` was written this session, tells the next session to handoff/reflect — the catch for a *crashed* session |

Three facts about this layer you must hold:

1. **Only two hooks deny.** `security-guard` and `version-guard` emit a `permissionDecision` of `deny`/`ask`. Every other hook emits *only* an advisory `systemMessage` or `additionalContext` and exits 0 — it can never block a tool or force continuation. A false positive on a byte-size heuristic must never halt real work.
2. **Everything fails open.** Any parse error, missing dir, or unexpected input exits 0 and does nothing. A bug in a guard can't crash a tool call. The axiom: a guard that crashes tools is worse than one that occasionally misses.
3. **The durability backstop is the catch for the un-graceful exit.** The auto-handoff loop is instruction-level — it depends on the model choosing to run `/handoff` on a wrap signal, and the Stop hooks only nudge. A *killed* session (crash, window close, context-wall `/compact`) never emits a clean Stop with the model still steering. `session-end-backstop.sh` is the event-driven catch for exactly that path, which is why it's wired on both `SessionEnd` and `PreCompact`.

A subtlety worth knowing early: the sensing signal (transcript **byte-size**) is the *weakest* coupling in the system, and the kit says so — bytes only loosely track real context fill (cache reads and compaction decouple them). It is explicitly a heads-up floor, never ground truth; the explicit "that's it" / `svaha` close stays the reliable wrap-up path. Don't mistake the byte counter for a measurement.

---

## 9. The role of guardrails — coherence as a first-class concern

Beyond the per-action hooks, Svaha treats **its own coherence as it grows** as a first-class problem — because a context system that rots is worse than none. The anti-drift machinery:

- **`SYNC_MAP.md` — the coupling map.** "Change X → also update Y." This is the maintenance view: rows that say, when you edit this trigger, these targets go stale or silently break. Rows marked **†** are *proven-by-incident* — a real drift was caught. After any structural edit, you scan this map and apply every row whose trigger you tripped. It is the single most important file for a maintainer to consult before changing anything structural.

- **`SYSTEM_MAP.md` — the data-flow view.** Where everything lives and how a session flows through it. Orthogonal to `SYNC_MAP` — and *themselves coupled*: edit one's model of the system, reconcile the other.

- **`drift-guard.py` — the edit-time backstop.** Fires only on structural-file edits and injects the relevant couplings, so a change surfaces what to update downstream *at edit time*. It is diff-gated on `CLAUDE.md` (suppressed on prose touching none of its tracked keywords) so most sessions pay nothing. Critically: it is a *reminder pointing back to the map*, not the map itself — it only knows the paths in its own pattern list, and fails open.

- **`coherence-check.py` — boot + stop integrity.** `--boot` asserts required files exist and commands match the registered set; `--stop` flags "plumbing edited but CHANGELOG not updated" and an audit-due delta.

- **`/audit` — the periodic sweep.** Tiered by churn (Tier 1 lightweight / Tier 2 full coherence). It is the *periodic backstop* for everything the edit-time guards miss: unpushed facts, contradictions, carry-forward debt and silent dropouts, sync-map coherence, guard health (hook registration + over-fire counts), and semantic rot. Understand its honest scope: it *spot-checks* a few high-blast couplings every few sessions — coherence is a sampled, manual sweep, not a continuously-enforced invariant.

The thing that stops the anti-drift machinery from itself drifting is partly mechanical (drift-guard fires on edits to `SYNC_MAP` and `drift-guard.py` themselves) and partly the same discipline applied recursively (the maps are coupled to each other). But be clear-eyed: at the bottom, the coherence guarantee rests on the model reading `SYNC_MAP` and applying it by hand, with `/audit` as a sampled backstop. It is *guidance the model is trusted to follow*, not an invariant the system enforces. (See §15 and §17.)

---

## 10. The purposes of boot, reflection, and handoff

- **Boot (`/session`, `/boot`)** exists to make a cold session warm *and to not trust the note that warms it*. It reads exactly two files, verifies the handoff's claims against reality, and refuses to silently re-run finished work. `/session` is the smart entry (auto-pick the lowest live slot / `list` / boot a specific `N`); `/boot` is the lower-level two-file sequence it wraps. The whole point is **resume-with-verification**, not resume-with-trust.

- **Reflection (`/reflect`)** is the lightweight close: the canonical memory pass + bug-log pass, with no `_NEXT`, no gauge, no closer. It is what a session runs when it reached a natural end with nothing to carry. It is also the *single source of truth* for the memory/bug logic that `/handoff` delegates to (handoff borrows reflect's steps but not its escalation gate — that one-directional borrow is what prevents a reflect→handoff→reflect loop).

- **Handoff (`/handoff`)** is the sealing act — the session wrap that mints the next frozen slot. Its first move is the **Warrant gate**: only genuine live carry-forward work warrants a `_NEXT` (and the seal); otherwise it downgrades to a reflection and closes with the hollow `◇ ◇ ◇` banner. When warranted, it writes the `_NEXT` (to a *unique* temp path — never a fixed `/tmp` name, the lesson of a cross-user `/tmp` collision that mis-minted a slot), retires the booted-from slot atomically, runs the continuity check (every move you booted with must be accounted for — done, carried, or dropped, never silently gone), and closes with the स्वाहा seal. The two close-banners are not decoration: `# स्वाहा` = a checkpoint was minted (resume-thread frozen, fresh session next); `# ◇ ◇ ◇` = a reflection (nothing carried, keep going or stop).

---

## 11. The architectural invariants

These must hold for the system to mean anything. For each, note whether it is **enforced** (a mechanism makes violation impossible/caught) or **claimed** (prose the model is trusted to honor) — this is the §0 lens applied to the invariant list.

1. **Frozen handoffs are never edited.** *Enforced* (rung 3): `version-guard.py` hard-blocks edits to `_NEXT_NNN.md`; `drift-guard.py` also warns.
2. **`next-write.sh` owns the slot number; mints are atomic.** *Enforced*: `noclobber` O_EXCL reserve + EXIT trap.
3. **A predecessor is never retired before its non-empty successor exists.** *Enforced*: `--consume` folds retire into mint with a non-empty assertion.
4. **Every retire is one idempotent, auditable operation.** *Enforced*: `next-consume.sh` is the single writer.
5. **The live set is computed, never eyeballed.** *Claimed* (hard rule in `CLAUDE.md`/`session.md`), *backstopped* by `next-live.sh` being the only correct source.
6. **A handoff's claims are verified before move 1 executes.** *Claimed*: RESUME-WITH-VERIFICATION is a boot *procedure* the model runs; `resume-line-guard.sh` backstops only the closer line, not the verification itself.
7. **A full handoff/seal is minted only for live carry-forward work.** *Claimed*: the Warrant gate is judgment.
8. **The seal स्वाहा appears only when `/handoff`/`/reflect` actually wrote a file.** *Claimed* (Core hard-guard) — a social/correctness convention, not hook-enforced.
9. **Conviction ≠ consequence; auto-escalations force a stop.** *Claimed*: the Risk Gate is a posture the model applies; the `settings.json` `ask`/`deny` lists enforce a *subset* (push, rm, secrets) deterministically.
10. **Secret reads and catastrophic ops are blocked.** *Enforced* (rung 3): `security-guard.py` + the `permissions.deny` list (double-layered).
11. **`SYSTEM_DIR` passed to a continuity script is the real root.** *Enforced* (for the writers): the continuity-writer family (`next-write.sh`, `next-consume.sh`, `next-boot.sh`, `external-done.sh`) guards on `_NEXT.md` and fails loud; `next-live.sh` guards on the `next/` dir. The Python guards do *not* guard on `_NEXT.md` — they resolve `<system-dir>` by the bounded `_LOADUP.md` search and fail *open*. So this enforcement lives with the writers, not the guards.
12. **Each content type has one canonical home.** *Claimed*: the content-placement table; `/audit` spot-checks.
13. **Always-loaded additions earn their weight.** *Claimed* (Deletion-First) — pure judgment, no check.

The pattern: **the file-and-plumbing invariants are enforced; the judgment-and-coherence invariants are claimed.** This is by design (you cannot hook a judgment call), but it is the thing a maintainer must never lose sight of. The strongest enforcement is exactly where a deterministic check is possible; everywhere else, the system *backstops* rather than *enforces*.

---

## 12. The assumptions behind major decisions

Some assumptions are derivable from the files; a few live mostly in the author's head and are worth surfacing explicitly so you don't accidentally violate them.

**Derivable from the files:**
- git + grep are sufficient ground truth — no DB/daemon/agents needed to verify a handoff.
- A model's self-reported confidence is *initially untrustworthy* and must be validated against outcomes before it earns execution authority (hence dormancy + the calibration loop).
- Declarative rules degrade; the fix is to climb the conviction ladder, not to restate louder.
- Work can be completed *outside* the tree, leaving no in-tree signal — a first-class completion class.
- A handoff content file is always written by the current user seconds before minting — so a >60-min-old or foreign-owned temp file is presumptively a stale/foreign `/tmp` leftover and is refused.
- BSD (macOS) and GNU (Linux) `stat`/`date` differ *and* an OR-chain fallback silently misfires on GNU — platform must be detected explicitly.

**Mostly in the author's head (state these to a new maintainer):**
- **Booting is read-only by invariant.** Nothing about resuming should mutate durable state except the advisory `.booted` hint. This is *why* a hard lock was rejected — a lock would break read-only-boot. If you ever add boot-time writes, you are violating an unstated axiom.
- **There is a human calibrator in the seat.** The calibration loop assumes the user will actually watch the conviction-vs-outcome correlation over many sessions and decide when to flip dormancy. The loop is not autonomous; it is human-in-the-loop by design.
- **The model's gradient is the adversary.** The entire behavior contract is built against the specific belief that the model will pick cheap/visible/helpful over expensive/correct unless structurally prevented. Read every "HARD RULE" and tripwire as a countermeasure to *that*, not as generic best practice.
- **The 2-strike threshold and the blast-radius cutoffs (~200 lines, new top-level dir) are chosen tradeoffs**, not derived constants — tune them knowingly.

---

## 13. The unusually elegant, the original, and the durable

**Unusually elegant (worth studying as craft):**
- **Verify-before-trust with nothing but git + grep.** Turns a trusted note into a checked contract using tools every repo already has — no infrastructure to build or keep alive.
- **Atomic mint-and-retire.** The consume-leak is closed not by a reminder but by making "create successor" and "retire predecessor" a single inseparable operation.
- **The EXIT trap on the empty reserve.** The `noclobber` reserve creates an empty file to win the race; the trap guarantees a crash never burns a slot number — the reservation's cost is fully reversible.
- **Sidecars.** Mutable lifecycle status (`.consumed`, `.booted`) coexists with a frozen artifact because status lives beside the file, never in it.
- **Registry-FIRST Step B.** Grepping the out-of-tree registry *before* any git-gated check, precisely because out-of-tree work commits nothing.
- **The seal as a falsifiable receipt.** स्वाहा may appear only when a file was actually written — a symbol that is also a proof-of-commit, enforced socially.
- **The *declined* boot-sweep-guard (read `ledger/DECISIONS.md`).** They shipped the registry but *declined* to add an enforcing hook, because on a fresh install there is no skip-proof anchor for it to key on and it would false-fire. Restraint as engineering.
- **The soft occupancy hint over a hard lock.** A deliberate choice of *less* mechanism — the hint needs no reaper because nothing depends on its accuracy. The opposite of gold-plating.

**Genuinely original (or original in combination):**
- The Verified Handoff as a *checked contract* rather than a trusted note.
- Parallel session **slots** (a set) designed from the ground up for concurrent amnesiac sessions sharing one folder with no lock.
- The **out-of-tree supersession registry** as a named completion class.
- The **svaha control-word** with positional disambiguation and a seal that doubles as a correctness guard.
- **Calibrating model self-assessment against recorded outcomes** — a closed loop built entirely out of plain-text files and grep.
- The **conviction ladder** (judgment rule → tripwire → hook) as an explicit rule-durability escalation path, with a mechanical trigger (≥2 reminders) for when a rule must change *form*.

The kit's own bet is **"the integration, not the individual ideas,"** and that framing is correct and honest. The individual primitives mostly exist somewhere; what has no clean prior art is the *fusion* — conviction-tagged decisions → outcome-stamped immutable handoff → git+grep verification at boot → calibration-miss detection → rule promotion, presented as three views of one loop.

**Likely to survive multiple model generations (the model-independent half):**
- *Verify-before-trust* grows **more** valuable as the writer/reader model gap widens — a handoff written by one generation and read by another is even less trustworthy as a bare note.
- *Immutable, append-only state with single-writer scripts* is a database-design principle that outlives any model and makes a smarter future model's mistakes recoverable.
- *Treating cross-session memory as an explicit, inspectable file artifact* — any cold-booting agent needs a durable, human-auditable resume point.
- *Human-adjudicated judgment gates* (WRITER-not-POLICY) — keeping "is this really done?" with a human matters *more* as models act more autonomously.
- *Separating correctness-confidence from safety-consequence* — a smarter model is more confident, which makes the decoupling more important, not less.
- *Mechanisms-beat-rules / earn-your-weight budgeting* — anti-entropy disciplines independent of model strength or window size.

What is **coupled to the substrate** (and will need a porting pass if Claude Code changes): every hook (event names, stdin JSON shape, matcher syntax), the `permissionDecision` field the two hard guards depend on (fail-open if absent — the most substrate-fragile load-bearing point), the byte-size transcript signal, the **`jq` dependency** (all six shell hooks parse stdin with `jq` and silently no-op without it — the single highest-likelihood silent failure on a fresh install), and the bash-3.2 portability tax. The healthy news: the irreplaceable IP is in the *portable* half (the continuity substrate), and the kit knows exactly which half is which — that is what `AGENTS.md` (the vendor-neutral mirror) is for.

---

## 14. Accidental vs. essential complexity

Be honest about this — the author is, in `DECISIONS.md`. Essential complexity is where the problem is genuinely this hard; accidental complexity comes from the substrate or from accreted fixes.

**Earned (essential, and well-built):**
- Atomic collision-safe minting — concurrency is a real, stated use case; a naive check-then-write genuinely loses a handoff.
- Verify-before-trust reconciliation — the lightest possible implementation of a genuinely necessary check.
- The kit-dir/system-dir split — prevents a real permission-storm and makes data relocatable.
- The out-of-tree registry — closes a real, subtle gap.
- The soft occupancy hint and the *declined* boot-sweep-guard — evidence the cost/benefit weighing is a live practice, not a slogan.

**Heavier than its problem (know this going in):**
- **The byte-size context layer.** Three hooks lean on the same byte-size proxy (with overlapping thresholds — 400/700 KB in the canary, 400 KB in the reflect nudge, 1.2 MB in the launchpad nudge), the proxy is admittedly poor, and `CLAUDE.md` already adds a *felt-degradation* override that does the real work. If it vanished, little would be lost.
- **The svaha ceremony.** The positional open/assent/close disambiguation and the seal hard-guard consume a strikingly large share of `CLAUDE.md` prose. As *engineering* it reduces to "a `/handoff` alias plus a rule about when to print one word." A lean adopter could delete ~90% of the ceremony and lose nothing functional. It is accidental complexity the project accepts *on purpose*, for identity reasons. (Respect that intent; just don't mistake volume for load-bearing function.)
- **The three-layer consume-leak defense (A/B/C).** Three mechanisms for one bug class — the signature of accreted scar tissue. Defensible (the failure is silent and costly), but a cleaner future design might collapse it.

**Accidental but unavoidable (substrate tax):**
- The four-way-duplicated `<system-dir>` discovery algorithm (the same bounded search hand-reimplemented in `coherence-check.py`, `drift-guard.py`, `resume-line-guard.sh`, `session-end-backstop.sh`, because hooks can't share a library cleanly). `SYNC_MAP` itself warns "change one, change all four." The four agree on the *search* but differ in *fallback*: `coherence-check.py` falls back to `KIT_DIR` as a self-check default, the others return nothing / stay silent — so when you edit one, check that its fallback still matches its caller's expectation, not just the search. A standing maintenance liability — handle with care.
- The bash-3.2 portability branches (macOS ships `/bin/bash` 3.2.57).
- `drift-guard`'s diff-gating machinery (exists only so the reminder isn't noise on every prose edit).

**The meta-pattern to name out loud:** a large fraction of total complexity is the *gap between claimed and enforced*. Because most of the loop is instruction-level, the system compensates with layered fail-soft backstops (drift-guard + version-guard; consume A/B/C; resume-line-guard + session-end-backstop). Each backstop is individually cheap, but in aggregate they form a thick mesh whose job is to catch the model when it doesn't follow the prose. A *more enforcing* substrate (if handoff-writing were a guaranteed lifecycle action) would let you delete most of it.

---

## 15. The single most important thing to internalize before you touch anything

Say it back to yourself: **most of this system is claimed by prose and only backstopped by code. The guards catch the model's lapses; they do not make the loop run.**

Concretely, the map of claimed vs. enforced:
- **Enforced by code (deterministic):** atomic mint, the `--consume` atomicity, single-writer retire, frozen-file deny, secret/catastrophic-op deny, the root guards, the `noclobber`/EXIT-trap concurrency safety, the JSON-validated settings merge.
- **Claimed by prose (model-trusted), with a fail-soft backstop:** RESUME-WITH-VERIFICATION, the Warrant gate, the live-set "never eyeball" rule, the closer-points-at-a-live-slot rule, the seal-only-on-handoff guard, the content-placement single-source-of-truth, SYNC_MAP follow-through.
- **Claimed by prose, with no backstop at all:** Deletion-First, the calibration loop's back half (outcome honesty, the manual `grep PARTIAL_MINUS` miss-detection, 2-strike promotion), conviction calibration.

The headline feature in the README — the self-calibrating loop — is the **least enforced** layer of the entire system. The durable, original engineering is *underneath* the headline, in the portable continuity substrate. This is not a criticism; it is the most important fact to hold when deciding what to change. **Do not "simplify" an enforced mechanism to match a claimed one, or assume a claimed mechanism is as robust as an enforced one.** When you strengthen the system, the highest-value move is almost always *converting a claimed invariant into an enforced one* (climbing the conviction ladder) — not adding a new claim.

---

## 16. The unresolved architectural questions

These are genuinely open after a thorough read. A new maintainer will hit them; have a position.

1. **What keeps the calibration loop alive?** `outcome:` is set by the model's own honesty, the calibration-miss surfaces only via a manual grep no hook runs, and 2-strike promotion is pure judgment. Worse, the `_NEXT` header has no explicit `conviction:` field — only `outcome:` — so "a high-conviction call that turned out FAILED" is reconstructed by inference (`PARTIAL_MINUS` as a proxy), not stored next to its outcome. The correlation the loop is built on cannot currently be computed mechanically. Is this a real feedback loop or a documented aspiration? If you want it real, the first move is persisting `conviction:` in the header and adding an `/audit` check that counts misses per conviction level.

2. **What is the contract with the Claude Code hooks API, and the migration plan when it changes?** The two hard guards fail *open* if `permissionDecision` is absent, and the whole sensing layer depends on on-disk transcripts and the stdin JSON shape. There is no version pin, no capability probe, no "your Claude Code is too old — guards are inert" warning beyond a code comment. A host upgrade could silently drop the safety floor. `doctor.sh` checks wiring and paths, not API-field support.

3. **How does the loop behave under genuinely contending sessions, beyond the mint race?** The mint TOCTOU is closed and occupancy is a soft hint that explicitly does not prevent double-booking. But two sessions on the same slot then race on *shared content files* (CHANGELOG, `_LOADUP`, indexes) with no guard but an advisory `touched:` warning. For single-user-on-one-Mac this is fine and intentional; a maintainer scaling to multi-machine sync needs to know the concurrency story is *advisory by design* and where a real lock would have to go.

4. **What is the upgrade story for a customized, drifted install?** The kit is firmware *and* the user is expected to heavily edit `CLAUDE.md` and fill `_LOADUP`. The section-patch path handles the marked block, but the merge semantics under *real* drift — a user who forked a `bin/` script, or edited inside the markers — are unspecified.

5. **Is `SYNC_MAP` a load-bearing mechanism or a hopeful document?** The coherence story rests on the model reading the map and applying it by hand; `drift-guard` only injects a reminder for paths in its own list, and `/audit` spot-checks 2–3 couplings every few sessions. The map is itself a file that must stay in sync with `SYSTEM_MAP`, `coherence-check`'s `PLUMBING_FILES`, and `drift-guard`'s `cat()` rows. When these diverge, what catches it? Today: a sampled manual sweep. That may be the right cost/benefit — but know that the coupling map is *guidance trusted to be followed*, not an enforced invariant.

There is also a small set of **already-present drift** in the shipped kit (the completeness spec exists in three diverging copies with no declared canonical — the most consequential, since `CLAUDE.md`'s own checklist omits `session.md`; the MANIFEST buckets the *shipped* `docs/index.html` in the same "cut" bullet as the genuinely-absent `compare.html`; `coherence-check.py --boot` checks fewer files than the spec it is coupled to; one stale "`/audit` check #6" cross-reference). These are documented in `FIRST_USER_READINESS.md` with fixes — flagged here because they are exactly the failure classes the kit's own coherence machinery is built to catch and cannot run against itself. They are a useful first PR for a new maintainer: low-risk, and they teach the SYNC_MAP discipline by doing it.

---

## 17. How to evolve Svaha without losing its philosophy — the maintainer's compact

This is the payoff. When you change Svaha, hold these — they are the operationalized philosophy:

1. **Before any structural edit, open `SYNC_MAP.md` and apply every coupling row you trip.** This is not optional hygiene; it is the one habit that keeps a growing config coherent. `grep -rn` the tree for any renamed name/path/field/count before you close. The `drift-guard` nudge is a reminder, not a substitute.

2. **Respect single-source-of-truth and do-not-restate.** If a procedure is canonical in one file, point at it from the other — never copy it. When you add content, consult the content-placement table for its one home. A patch to a downstream copy creates a fork.

3. **Earn always-loaded weight (Deletion-First).** Every addition to `CLAUDE.md` is paid by every future session forever. Cite an offsetting trim or a one-line net-add justification. Bias to fewer, sharper primitives over more rules. The kit's own legibility ("afternoon-readable") is a feature you can destroy by accretion.

4. **Prefer climbing the conviction ladder to adding a rule.** If something keeps going wrong, don't write a louder rule — change its form (judgment rule → tripwire → hook). The ≥2-reminder heuristic is your trigger. The highest-value contributions convert a *claimed* invariant into an *enforced* one.

5. **fix → diagnose → prevent, every time.** Fixing an error is never one step. After the fix: diagnose exactly why it happened, then build a concrete mechanism that makes the class impossible or reliably caught. "It won't happen again" without a mechanism is not prevention. The prevention is *pre-authorized* — it follows directly from the diagnosis; build it as part of closing the loop.

6. **Keep guards fail-open and allow-by-default.** Never let an advisory hook block. Never let a guard crash a tool. Act only on small, high-confidence patterns. A guard that fires on normal work trains the user to disable it.

7. **Honor the firmware/user-owned boundary.** Changes that should ship to all users go in firmware (`bin/`, `commands/`, `hooks/`, the `SVAHA:BASE` block, `settings.json.snippet`) — and a firmware change to `CLAUDE.md`'s base block means bump `VERSION` and add a `PATCHES.md` entry. Never touch the user-owned layer (below the end-marker, project data) in a patch.

8. **bash 3.2 or it doesn't ship.** macOS `/bin/bash` is 3.2.57. No `mapfile`, no associative arrays, no process substitution under `set -e`. Detect BSD-vs-GNU `stat`/`date` explicitly (an OR-chain silently misfires on GNU). Run `bash -n` and test on macOS.

9. **No hard deletes; archive before mutating.** Retire to `_ARCHIVE/` (date/version-stamped) before overwriting a frozen or canonical artifact, even when you're sure the change is safe. "I was sure it was fine" is not a recovery path.

10. **When in doubt about whether something is safe to change, apply the §0 lens.** Is it enforced or claimed? An enforced mechanism is load-bearing — treat its code as a contract. A claimed mechanism is prose the model follows — improving it usually means *enforcing* it, not deleting it.

And the meta-rule that contains all the others: **assume every unusual choice has a design reason, and find it before you change it.** The `ledger/DECISIONS.md` log is where the road-not-taken lives (the hard lock that was rejected, the boot-sweep-guard that was declined) — read it before you "fix" something that looks over- or under-built. Much of what looks like accidental complexity is a scar from a specific, dated failure, and the scar is load-bearing.

---

## 18. A reading order for going deeper

When you need the ground truth behind any claim in this guide:

1. `README.md` — the thesis and the loop, in the author's framing.
2. `CLAUDE.md` — the whole behavior contract. Read it once, fully; it is the system in one file.
3. `SYSTEM_MAP.md` then `SYNC_MAP.md` — the data-flow view, then the coupling view.
4. `_NEXT.md` — the Verified Handoff spec and why each header field exists.
5. `commands/boot.md` (RESUME-WITH-VERIFICATION) and `commands/handoff.md` (the Warrant gate + write mechanics).
6. `bin/next-write.sh`, `next-consume.sh`, `next-live.sh`, `external-done.sh` — the continuity machinery; the comments carry the incident history.
7. `bin/security-guard.py`, `version-guard.py`, `drift-guard.py`, `coherence-check.py` — the enforcement layer.
8. `ledger/DECISIONS.md` — the roads not taken. Short, and disproportionately illuminating.
9. `MANIFEST.md` — the inventory and the Core/bolt-on distinction.
10. `docs/CREDITS.md` — what was folded in vs. invented, stated honestly.
11. `setup.sh`, `bin/merge-settings.py`, `bin/doctor.sh` — the install + firmware-update + safe-merge machinery. The first-user risk surface lives here; pair with `FIRST_USER_READINESS.md`.

*One caveat on this reading order:* `MANIFEST.md` and the completeness spec currently carry the minor drift noted in §16 (and detailed in `FIRST_USER_READINESS.md §7`) — treat those two as inventory-to-reconcile, not gospel, until fixed.

---

*The final test for this guide: if a fresh frontier model, given only this document, could read a pull request to Svaha and tell whether it strengthens the loop or quietly breaks it — without asking the author how the system works — then the mental model transferred. The one sentence that most determines that: most of Svaha is claimed by prose and backstopped by code; the durable engineering is the portable continuity substrate; and the way to strengthen it is to turn claims into enforcement, never the reverse.*
