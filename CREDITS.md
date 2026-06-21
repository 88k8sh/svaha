# Credits & acknowledgments

Throughline is built to **compose with** community work, not replace it. It reuses no code from the projects below — only widely-shared ideas and the standardized Claude Code plugin format. Each is an independent project under its own license; go support them.

- **Superpowers** — Jesse Vincent (obra) · <https://github.com/obra/superpowers> — methodology-as-skills (brainstorm → design → TDD → verify). Throughline is the cross-session spine a skill library runs on. Pair them.
- **Context7** — Upstash · <https://github.com/upstash/context7> — an MCP server for up-to-date library docs. Complementary: Context7 keeps Claude current on *external* facts; Throughline on *your* project.
- **TLDR-code** — parcadei — semantic code comprehension over a large repo. Complementary: Throughline's recall is for evidence/project context and does **not** do code analysis. Point TLDR-code at the source; Throughline carries the continuity.
- **claude-starter-kit** — mp-web3 · <https://github.com/mp-web3/claude-starter-kit> — inspired the runtime security-guard idea (a `PreToolUse` hook that blocks dangerous calls). `bin/security-guard.py` is an independent implementation.
- **claude-code-mastery-project-starter-kit** — TheDecipherist · <https://github.com/TheDecipherist/claude-code-mastery-project-starter-kit> — one of the starter kits surveyed while scoping what Throughline should and shouldn't be.

And **Claude Code** (Anthropic) — whose `CLAUDE.md`, hooks, and slash-command surfaces make all of this possible.

## Ideas folded in

Throughline integrates patterns explored across the ecosystem — most load-bearing: **frozen-artifact version enforcement**, **resume-with-verification** (re-check the prior state instead of trusting the handoff), the **premortem Tiger / Paper-Tiger framing**, **2-strike correction → rule promotion**, and **reversibility as a required field**. Each was written fresh, not copied. Sources surveyed include parcadei/Continuous-Claude-v3 (closest analog — ledger + immutable handoffs), KbWen/agentic-os (evidence-gated governance; the only one shipping a real same-file lock), justnau1020/claude-os, TheDecipherist's starter kit, and dlowenth/claude-code-build-framework.

The individual ideas are well-explored; Throughline's bet is the **integration** — parallel-slot frozen handoffs + edit-time coherence guardrails + an optional decision layer, fused with the author's own handoff loop into one self-calibrating circuit where the conviction tag, the Verified Handoff, and the Risk Gate are three views of the same loop.

*If something here builds on your work and isn't credited, open an issue and it'll be fixed.*
