# Svaha Core — Manifest

The distilled, source-vetted Core of Svaha: afternoon-readable, fully functional,
charter-clean. Built from the full kit by keeping every safety/continuity primitive verbatim,
slimming accretion, and cutting four enhancement/marketing components to the bolt-on tier.

---

## The five layers (completeness spec)

### 1 · Handoff loop
| File | Role |
|---|---|
| `_NEXT.md` | Canonical `_NEXT` format + Verified-Handoff field semantics (single source of truth) |
| `templates/_LOADUP.template.md` | Boot context-bootstrap skeleton (§0–8); `/init` copies it to the system root as `_LOADUP.md` (shipped under `templates/`, renamed, so the kit root is not a resolver anchor — v0.6.2) |
| `commands/boot.md` | `/boot` — two-file boot + RESUME-WITH-VERIFICATION (steps A–D) |
| `commands/session.md` | `/session` — smart entry (auto-pick / list / boot a slot) |
| `commands/handoff.md` | `/handoff` — session wrap; Warrant gate, Continuity check, read-back |
| `commands/reflect.md` | `/reflect` — memory + bug-log pass (handoff steps 4–5 delegate here) |
| `commands/foldin.md` | `/foldin` — adopt an ungoverned conversation into the system |
| `commands/init.md` | `/init` — scaffold a fresh project's data layer (per-project, runs once) |
| `bin/next-write.sh` | Atomic, collision-safe `_NEXT_NNN` writer |
| `bin/next-live.sh` | Single source of truth for the live-session set |
| `bin/next-boot.sh` | Writes the advisory `_NEXT_NNN.booted` occupancy hint at boot (double-booking soft-guard) |
| `bin/external-done.sh` | Single-writer for the out-of-tree supersession registry (read first by `boot.md` Step B) |
| `templates/_NEXT_001.md` | Seed handoff; `/init` copies it to `<system-dir>/next/_NEXT_001.md` (shipped under `templates/`, not at the kit root — v0.6.2) |

### 2 · Guardrail shell
| File | Role |
|---|---|
| `bin/security-guard.py` | **SAFETY** — denies secret reads + catastrophic ops (charter §1.4/§1.5) |
| `bin/version-guard.py` | **SAFETY** — hard-blocks edits to frozen artifacts |
| `bin/drift-guard.py` | PreToolUse coherence guard (prevent layer) — wired to SYNC_MAP |
| `bin/coherence-check.py` | Boot integrity check + `--stop` exit check |
| `commands/audit.md` | `/audit` — periodic drift/coherence sweep (Tier 1 / Tier 2) |
| `SYNC_MAP.md` | Coupling map (change X → update Y) |
| `SYSTEM_MAP.md` | Data-flow view (what file does what) |

### 3 · Canary hooks
| File | Role |
|---|---|
| `hooks/context-canary.sh` | PostToolUse — byte-size context-fill canary (yellow/red) |
| `hooks/launchpad-nudge.sh` | Stop — once-per-heavy-session wrap-up nudge |
| `hooks/memory-reflect.sh` | Stop — tiered nudge to run `/reflect` |
| `hooks/resume-line-guard.sh` | Stop — validates the session-closer points at a live `_NEXT` |
| `hooks/session-end-backstop.sh` | SessionEnd/PreCompact — durability catch for killed sessions |
| `hooks/session-start-marker.sh` | SessionStart — stamps the per-session start marker |
| `settings.json.snippet` | The install contract that wires the guards + hooks |

### 4 · Memory
| File | Role |
|---|---|
| `memory/MEMORY.md` | Behavioral-memory index |
| `memory/README.md` | Write-guard + content-placement operating spec |

### 5 · Ledger
| File | Role |
|---|---|
| `ledger/CHANGELOG.md` | Master system log (seeded with the Core distillation entry) |
| `ledger/DECISIONS.md` | Design decisions + alternatives |
| `ledger/LESSONS.md` | Named lessons from incidents |
| `ledger/session-fixes.md` | Bugs caught + fixed |
| `ledger/USER_TASKS.md` | Human-only tasks |
| `ledger/audit-state.md` | Audit counter |
| `ledger/drift-guard-evidence.md` | Guard catches log |
| `ledger/drift-guard-overfires.md` | Over-fire log (audit reads for tighten signal) |
| `ledger/EXTERNAL_DELIVERABLES.md` | Out-of-tree supersession registry (append-only; written by `bin/external-done.sh`, read by `boot.md` Step B) |
| `_ARCHIVE/README.md` | Graveyard for retired files |

---

## Behavior contract + docs
| File | Role |
|---|---|
| `CLAUDE.md` | The always-loaded behavior contract (core safety skeleton + optional Operator layer) |
| `AGENTS.md` | Vendor-neutral mirror of `CLAUDE.md` for non-Claude agents |
| `README.md` | Front door |
| `docs/CREDITS.md` | Provenance ledger |
| `LICENSE` | MIT |
| `setup.sh` | Non-destructive installer (companions are print-only) |
| `.claude-plugin/plugin.json` | Plugin-system manifest (its `version` is the single version source the marketplace entry inherits) |
| `.claude-plugin/marketplace.json` | Single-plugin marketplace (`source: "./"`) — lets users `/plugin marketplace add 88k8sh/svaha` + `/plugin install svaha@svaha`. Additive convenience; `setup.sh` never reads it (v0.7.0) |
| `hooks/hooks.json` | Plugin hook wiring — the 10 hooks via `${CLAUDE_PLUGIN_ROOT}`; auto-discovered under the plugin model. Invisible to `setup.sh`, which wires via `settings.json.snippet` instead (v0.7.0) |
| `.svaha-kit` | Kit-distribution marker — makes the continuity writers, `/init`, and `coherence-check.py` refuse to treat the kit root as a user `<system-dir>` (the kit-as-system-dir guard, v0.6.2) |
| `VERSION` | Kit semantic version — read by `setup.sh` and `bin/doctor.sh` |
| `PATCHES.md` | User-facing changelog for CLAUDE.md base rule and firmware changes |
| `CONTRIBUTING.md` | Firmware vs user-owned layer model; PR requirements for upstream fixes |

---

## Cut from Core (relocated to bolt-on / published-site tier)
- `bin/context-pct.sh` — statusLine measured-% bridge (byte-size fallback covers it)
- `hooks/premortem-suggest.sh` — advisory hook re-raising an existing CLAUDE.md rule
- `docs/index.html`, `docs/compare.html` — marketing landing pages
