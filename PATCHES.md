# Svaha — Patch Notes

Changes to the Svaha base rules (CLAUDE.md) and firmware files by version.

**To update:** `cd svaha-core && git pull && ./setup.sh`

`setup.sh` detects the `<!-- SVAHA:BASE -->` markers in your `~/.claude/CLAUDE.md` and patches only the Svaha-owned block — your customizations below `<!-- SVAHA:BASE:END -->` are never touched. Commands and hooks are already updated on each `./setup.sh` run (they back up before overwriting).

---

## v0.5.0 — 2026-06-25

**Baseline release — versioning and patch infrastructure introduced.**

This is the first versioned release. All prior work merged into this baseline.

### What changed

- **Section markers added to `CLAUDE.md`** — `<!-- SVAHA:BASE:START:v0.5.0 -->` before `## Boot` and `<!-- SVAHA:BASE:END -->` after the final rule. These enable the section-patch path in future `./setup.sh` runs.
- **`VERSION` file** — single-line semantic version; read by `setup.sh` and `bin/doctor.sh`.
- **`setup.sh` — three-path CLAUDE.md logic:**
  - Fresh install → writes kit template as before
  - Markers found → patches only the Svaha base block (new)
  - No markers (legacy install) → offers wholesale replace as before
- **`bin/doctor.sh`** — version check added as check #0.

### Upgrading from a pre-v0.5.0 install

Run `git pull && ./setup.sh`. When prompted about `CLAUDE.md`, answer `y` to overwrite — this adds the markers that unlock automatic section-patching in all future updates. Your existing Svaha rules will be in the marked block; add any project-specific rules below `<!-- SVAHA:BASE:END -->` after.
