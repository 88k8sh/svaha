# Plugin Packaging Recon — Svaha as a Claude Code Plugin

*Feasibility recon, not an implementation. No existing files were changed to produce this. Sources for the plugin format: the official Claude Code docs — [plugins-reference](https://code.claude.com/docs/en/plugins-reference.md), [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces.md), [discover-plugins](https://code.claude.com/docs/en/discover-plugins.md). Spec facts are marked **[V]** (verified in those docs) or **[I]** (inferred); the Svaha-side analysis is my own.*

## TL;DR

Svaha is **partially plugin-shaped already** — it ships `.claude-plugin/plugin.json` and its `commands/`, `hooks/`, `bin/` are in the conventional locations. The parts that make Svaha *work as a plugin* (its hooks) need one translation file, and the parts that make Svaha *Svaha* (the `CLAUDE.md` behavior contract) and *safe-by-default* (the `settings.json` permission floor) **cannot be delivered by a plugin at all** — plugins are declarative, cannot run an install script, cannot write `settings.json`, and cannot install a global `CLAUDE.md`.

**Recommendation: ship both, honestly scoped.** Keep `setup.sh` as the canonical full install (the only path that delivers the contract + the permission floor). Add a thin, additive plugin/marketplace entry as a convenience for the parts that map cleanly (commands + hooks), with docs that say plainly what the plugin path does *not* install. A pure-plugin Svaha would be a lobotomized Svaha.

---

## 1. What files are required for a marketplace entry?

**[V]** A repo becomes a Claude Code plugin marketplace by adding **`.claude-plugin/marketplace.json`** at the repo root. Required fields:

| Field | Required | Notes |
|---|---|---|
| `name` | yes | kebab-case; users type it: `/plugin install <plugin>@<name>` |
| `owner` | yes | object with required `owner.name` (optional `email`) |
| `plugins` | yes | array; each entry needs `name` + `source` |

A plugin `source` can be a relative path (`"./"` or `"./plugins/x"`, git-based marketplaces only), or an object: `{source:"github", repo:"owner/repo", ref?, sha?}`, `git`/`url`, `git-subdir`, or `npm`. Users add a marketplace with `/plugin marketplace add owner/repo` (also git URL, local path, or remote URL) and install with `/plugin install <name>@<marketplace> [--scope user|project|local]`.

For Svaha: the **same repo can double as a single-plugin marketplace** — `marketplace.json` listing one plugin whose `source` is `"./"`.

## 2. What files are required inside an individual plugin?

**[V]** Only **`.claude-plugin/plugin.json`** with at minimum a `name` (the manifest is technically optional if you rely purely on autodiscovery, but you want it for metadata). Everything else is auto-discovered from conventional directories **at the plugin root** (never inside `.claude-plugin/`):

| Component | Default location | Discovery behavior |
|---|---|---|
| commands | `commands/*.md` | replaces default |
| agents | `agents/*.md` | replaces default |
| skills | `skills/<name>/SKILL.md` | adds to default |
| hooks | `hooks/hooks.json` (or inline `"hooks"` in plugin.json) | merged |
| MCP servers | `.mcp.json` (or inline `"mcpServers"`) | merged |
| executables | `bin/` | added to the Bash tool PATH |

**[V]** Hook commands and config must reference bundled files via **`${CLAUDE_PLUGIN_ROOT}`** (the plugin's install dir — changes on update) rather than absolute paths; **`${CLAUDE_PLUGIN_DATA}`** is a per-plugin dir that survives updates (for logs/state). Plugins are copied to a cache (`~/.claude/plugins/cache/<id>/`) and **cannot reference files outside their own directory** in declared config — but a *running* hook process still executes with full user privileges and can read the project tree (this matters for Svaha's `<system-dir>` discovery — see Q7).

## 3. Which parts of Svaha map cleanly?

| Svaha part | Maps? | Notes |
|---|---|---|
| **commands** (`commands/*.md`: boot, session, handoff, reflect, audit, foldin, init) | ✅ **clean** | Already in the exact plugin layout; auto-discovered. They'd be namespaced (`/svaha:handoff` etc.) **[I]** — minor UX change from the bare `/handoff`. |
| **hooks** (6 `.sh` + the 4 Python guards wired as PreToolUse/Stop/etc.) | ⚠️ **with a translation** | The *scripts* are fine in `hooks/` and `bin/`. But Svaha currently declares the wiring in `settings.json.snippet` (user merges it). The plugin model declares wiring in **`hooks/hooks.json`** using `${CLAUDE_PLUGIN_ROOT}/...` instead of the baked `<kit-dir>`. This file does not exist yet — it's the one real artifact needed to make hooks work as a plugin. |
| **bin/ scripts** | ✅ **clean** | `bin/` is auto-added to PATH; the guard/handoff scripts resolve their own location from `__file__`, so they keep working from the cache dir (one caveat: log paths, Q7). |
| **agents** | n/a | Svaha ships none. Nothing to map. |
| **skills** | n/a | Svaha ships none. (Its slash commands are *commands*, not skills. Optionally some could be re-expressed as skills, but that's a redesign, not a port.) |
| **settings** (`settings.json.snippet`: hooks + the allow/ask/deny permission posture + `additionalDirectories`) | ❌ **does not map** | **[V]** A plugin cannot write the user's `settings.json`. The *hooks* half moves to `hooks.json`, but the **permission posture** (deny secret reads, ask on push/rm, edit-mode A/B, `additionalDirectories`) **cannot be delivered by a plugin.** A plugin may declare `userConfig` (prompts the user, writes to a sandboxed `pluginConfigs` block) — not arbitrary permission rules. |
| **setup.sh** | ❌ **does not map** | **[V]** Plugin install is **declarative-only — no install script runs.** setup.sh's path-baking is *replaced* by `${CLAUDE_PLUGIN_ROOT}` (a genuine simplification), but its stateful jobs — generate/merge `settings.json`, install/section-patch `CLAUDE.md` — have **no plugin equivalent.** |

## 4. Which parts do not map cleanly?

The non-mapping set is small but it is the *load-bearing* set:

1. **`CLAUDE.md` — the behavior contract (the heart of Svaha).** **[V]** A plugin **cannot install a global/project `CLAUDE.md`**; a `CLAUDE.md` at a plugin root is not loaded as context. Plugins contribute context via skills/agents/hooks, which load *on invocation*, not *every session*. Svaha's contract is defined by being **always-loaded** — the Risk Gate, the operator layer, the boot/handoff/seal rules. There is no plugin mechanism for an always-on contract. (A skill could carry the rules, but only when invoked — that changes the contract's fundamental nature.)
2. **The `settings.json` permission floor.** The safe-by-default `deny`/`ask` posture is the *first* layer of Svaha's double-layered secret/destructive protection (the second being `security-guard.py`). A plugin can ship the guard hook but **not the declarative floor** — so a plugin-only install is *less* safe-by-default (see Q7).
3. **`setup.sh`'s stateful actions** — settings merge, CLAUDE.md install + SVAHA:BASE section-patching, and the `doctor.sh` wiring verification. Plugin updates replace firmware versioning, but the contract-install and permission-merge steps have no declarative analog.
4. **The `<kit-dir>` baking** — *positively* obviated by `${CLAUDE_PLUGIN_ROOT}` (the plugin system owns the machinery path). The kit-dir/system-dir split survives intact: kit-dir → `${CLAUDE_PLUGIN_ROOT}`, system-dir → still runtime-resolved per project via the bounded `_LOADUP.md` search. This is the one part that gets *cleaner* as a plugin.

The per-project data layer (`/init` scaffolding `next/`, `ledger/`, `memory/`, `_LOADUP.md`) maps fine — `/init` is just a command the user runs after install; it works identically either way.

## 5. Plugin vs. marketplace vs. GitHub script vs. both?

**Both — `setup.sh` as canonical, plugin/marketplace as an honestly-scoped convenience.** Reasoning:

- **A pure plugin is insufficient.** It cannot deliver the two things that define Svaha: the always-loaded `CLAUDE.md` contract and the permission floor. Distributing Svaha *only* as a plugin would ship the plumbing without the behavior — users would get slash commands and hooks but not the decision discipline, and a weaker safety posture. That is not Svaha.
- **`setup.sh` remains the only complete path.** It is the only mechanism that installs the contract, merges the permission posture, and section-patches `CLAUDE.md` on upgrade.
- **A marketplace is cheap and worth adding.** One `marketplace.json` lets users `/plugin marketplace add 88k8sh/svaha` then `/plugin install svaha@svaha` — a discovery/convenience win for the cleanly-mapping half (commands + hooks).
- **The plugin path must document its own incompleteness** loudly: "this installs the commands and hooks; you still need `cp CLAUDE.md ~/.claude/CLAUDE.md` and the permission posture." Otherwise users get a silently-half-installed Svaha — exactly the failure class `FIRST_USER_READINESS.md` is about.

Net: **GitHub script (primary) + plugin & marketplace (additive convenience).** Not plugin-only.

## 6. Smallest safe path to plugin-installability without breaking `setup.sh`

Purely **additive** — two new files, zero edits to existing install machinery:

1. **Add `hooks/hooks.json`** — translate the `settings.json.snippet` hooks block into the plugin hook schema, swapping baked `<kit-dir>` for `${CLAUDE_PLUGIN_ROOT}` (e.g. `python3 "${CLAUDE_PLUGIN_ROOT}/bin/security-guard.py"`, `bash "${CLAUDE_PLUGIN_ROOT}/hooks/context-canary.sh"`). This is the single artifact that makes the hooks fire under the plugin model. The existing `.claude-plugin/plugin.json` then needs no change (default `hooks/hooks.json` is auto-discovered) — or add an explicit `"hooks": "./hooks/hooks.json"` for clarity.
2. **Add `.claude-plugin/marketplace.json`** — list the one plugin with `source: "./"`.

Why this is safe and non-breaking:
- `marketplace.json` and `hooks/hooks.json` are **invisible to `setup.sh`** — it copies `commands/` + `hooks/*.sh` and wires via `settings.json.snippet`; it doesn't read either new file. The two install paths coexist.
- No moves, no renames — the scripts are already where both models expect them.

**The one hazard to document, not a blocker:** if a user installs via the plugin **and** runs `setup.sh`, the hooks get wired **twice** (once in `~/.claude/settings.json`, once by the plugin) and fire double. So the guidance must be **plugin XOR setup.sh for the hooks** — pick one path. (The Python guards are idempotent in effect but would emit duplicate denials/messages; the byte-size hooks would double-fire their nudges.)

## 7. Privacy / security concerns if Svaha becomes a plugin

1. **Weaker safe-by-default posture (the real one).** Svaha's secret-read / destructive-op protection is **double-layered**: `permissions.deny` (declarative, first cut) + `security-guard.py` (enforcing hook). A plugin can ship the hook but **not** the declarative floor. So a plugin-installed Svaha silently drops to *one* layer unless the user manually adds the deny/ask rules. **This is a genuine security regression** versus `setup.sh`, and must be stated at install.
2. **Hooks run with full user privileges, unsandboxed, no per-hook gate.** **[V]** This is true of all plugins, and Claude Code shows an install-time warning ("Anthropic does not control… cannot verify"). Svaha's hooks are benign, but the marketplace trust model means a user is trusting arbitrary code execution. Svaha should be transparent that its hooks run Python/bash and read the transcript file (byte-size sensing). **[I]** Hooks fire on their triggering event, **not** on install.
3. **Telemetry.** **[V]** Claude Code shows a per-plugin "context cost" estimate; **[I]** no documented transmission of plugin usage telemetry. Svaha itself collects and sends nothing (local-first); the only egress remains the optional, manual `git push`. The plugin system does not change Svaha's local-first promise — but that promise should be restated for plugin users, who may assume a marketplace plugin "phones home."
4. **Log-path drift.** `security-guard.py` / `version-guard.py` write logs to `<kit-dir>/ledger/*.jsonl` (relative to `__file__`). Under the plugin model `__file__` is in the cache dir, which can be wiped on update — guard logs would be lost. Fix at port time: write to `${CLAUDE_PLUGIN_DATA}` (the update-surviving dir). **[I]**
5. **`<system-dir>` discovery still works** — the hooks walk up from the session CWD for `_LOADUP.md`, and a running hook process is not path-restricted to the plugin dir (the path-traversal restriction applies to *declared config references*, not to what an executing hook reads). So per-project data resolution is unaffected. **[I]**

## 8. Files to add / move / rename

| Action | File | Purpose |
|---|---|---|
| **ADD** | `.claude-plugin/marketplace.json` | Makes the repo a marketplace listing the svaha plugin (`source: "./"`). |
| **ADD** | `hooks/hooks.json` | Declares the 6 shell hooks + 4 Python guard wirings using `${CLAUDE_PLUGIN_ROOT}`. The one artifact that makes hooks work as a plugin. |
| **EDIT (optional)** | `.claude-plugin/plugin.json` | Optionally add explicit `"hooks": "./hooks/hooks.json"` and/or a `userConfig` for the edit-mode A/B choice. Not required if defaults are used. Already valid today. |
| **EDIT (at port time)** | `bin/security-guard.py`, `bin/version-guard.py` | Point logs at `${CLAUDE_PLUGIN_DATA}` so they survive plugin updates. Minor. |
| **No move / no rename** | `commands/`, `hooks/*.sh`, `bin/` | Already in the conventional plugin locations. |
| **Cannot be shipped by the plugin** (stays in `setup.sh` / Track A / a command) | `CLAUDE.md`, the `settings.json` permission posture | No plugin mechanism exists; document the manual step. |

---

## Bottom line for a maintainer

The cleanly-mapping half (commands + hooks) ports with **two additive files and zero breakage**, and `${CLAUDE_PLUGIN_ROOT}` actually *removes* the `<kit-dir>`-baking complexity. The non-mapping half is the important half: a plugin **cannot install the behavior contract or the permission floor**, so the plugin path is inherently a *convenience layer over an incomplete install*, never a replacement for `setup.sh`. Ship both, make `setup.sh` canonical, and make the plugin path state plainly what it leaves out — anything less reproduces the silent-half-install failure mode Svaha is otherwise built to prevent.
