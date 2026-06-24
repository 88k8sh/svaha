#!/usr/bin/env python3
"""
drift-guard.py — PreToolUse hook for Edit | Write | MultiEdit (the prevent layer).

Fires ONLY when a *structural* file is about to be edited; injects the relevant
SYNC_MAP couplings so cross-file drift is caught at edit-time, not after a break.
Silent on every non-structural edit, so most sessions pay nothing.

The guardrails guard (CLAUDE.md) is DIFF-GATED: suppressed on prose edits that
touch none of its tracked items (boot phrases / deny-fence / egress / model tiers).
settings.json is never gated. Fail-open everywhere uncertain (Write full-file,
MultiEdit, unreadable input) so a real drift can never be silently missed.

Wired in ~/.claude/settings.json under hooks.PreToolUse (matcher "Edit|Write|MultiEdit").
The structural-path list is itself a coupling — see SYNC_MAP.md. Never blocks; any
error exits 0 so a bug in the guard can't stop an edit.

SETUP: edit WORKSPACE_ROOTS, EXCLUDED_PREFIXES, and the cat() coupling rows below
to match your project's structural files.
"""
import json
import re
import sys
from pathlib import Path


# Kit root (where this guard + the rest of bin/ live — resolved from __file__,
# never baked) and the per-project data root (discovered at runtime: the nearest
# ancestor of CWD holding _LOADUP.md). Both count as in-scope workspaces; an edit
# anywhere else is ignored, so the guard never fires on an unrelated repo.
KIT_DIR = Path(__file__).resolve().parent.parent


def _discover_system_dir():
    # Bounded: up-scan (CWD + ancestors) then a one-level down-scan (CWD's immediate
    # children, unambiguous match only) so a launch in a workspace that *contains* the
    # system resolves too. Never recursive — no filesystem-exploration storm.
    try:
        start = Path.cwd().resolve()
    except Exception:
        return None
    for cand in [start, *start.parents]:
        if (cand / "_LOADUP.md").is_file():   # regular file only — matches the shell `-f`
            return cand
    try:
        # dedup by resolved real path so a symlink twin counts once (no false ambiguity)
        kids = {c.resolve() for c in start.iterdir()
                if c.is_dir() and not c.name.startswith(".") and (c / "_LOADUP.md").is_file()}
    except Exception:
        kids = set()
    if len(kids) == 1:
        return next(iter(kids))
    return None


def emit(text):
    """Inject a non-blocking reminder into the model's context for this tool call."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never block on a parse error

    tool_input = data.get("tool_input") or {}
    path = (tool_input.get("file_path") or "")
    p = path.replace("\\", "/")
    if not p:
        sys.exit(0)

    # ── scope strictly to this workspace — never fire on unrelated repos ──
    # In-scope = the kit clone (machinery) + the current project's data root
    # (discovered) + ~/.claude. Both kit-dir and system-dir are auto-resolved — no
    # baked path to hand-edit.
    # Resolve the EDIT path too before the substring test: KIT_DIR and the discovered
    # sysdir are both .resolve()d, so an edit addressed via a symlinked path (/tmp vs
    # /private/tmp, a synced/aliased root, a symlinked kit) wouldn't substring-match the
    # resolved root — and the guard would silently skip a real structural edit. resolve()
    # canonicalizes the existing dir prefix even for a not-yet-created file. Fail-open.
    try:
        p_scope = str(Path(path).resolve()).replace("\\", "/")
    except Exception:
        p_scope = p
    sysdir = _discover_system_dir()
    WORKSPACE_ROOTS = [str(KIT_DIR) + "/", "/.claude/"]
    if sysdir is not None:
        WORKSPACE_ROOTS.append(str(sysdir) + "/")
    if not any(root in p_scope for root in WORKSPACE_ROOTS):
        sys.exit(0)

    # Sub-projects: skip files inside known non-live directories.
    # These share filenames with live plumbing but are not part of the running system
    # (e.g. starter packages, reference snapshots, archived copies). Absolute paths.
    EXCLUDED_PREFIXES = [
        # "/path/to/a/reference-copy/",  # ← uncomment and add as needed
    ]
    if any(prefix in p for prefix in EXCLUDED_PREFIXES):
        sys.exit(0)
    # ────────────────────────────────────────────────────────────────────────────

    # Frozen handoffs: editing a _NEXT_NNN.md is itself a rule violation.
    if re.search(r"/_NEXT_\d+\.md$", p):
        emit("⚠ FROZEN handoff: _NEXT_NNN.md files are never edited after creation "
             "(treat like a commit). Put corrections in a NEW numbered file via "
             "bin/next-write.sh. See _NEXT.md spec.")
        return

    # Extract the text this edit actually changes, so the guardrails guard can fire on
    # relevance instead of on every CLAUDE.md prose edit. Edit → old+new strings;
    # Write → content; MultiEdit → all edit strings. If it can't be read cleanly,
    # treat as unknown and fail OPEN (fire) — a real drift must never be missed.
    changed_known = False
    _parts = []
    if isinstance(tool_input.get("new_string"), str) or isinstance(tool_input.get("old_string"), str):
        _parts.append(tool_input.get("new_string") or "")
        _parts.append(tool_input.get("old_string") or "")
        changed_known = True
    elif isinstance(tool_input.get("content"), str):
        _parts.append(tool_input["content"])
        changed_known = True
    elif isinstance(tool_input.get("edits"), list):
        for _e in tool_input["edits"]:
            if isinstance(_e, dict):
                _parts.append(_e.get("new_string") or "")
                _parts.append(_e.get("old_string") or "")
        changed_known = True
    changed = "\n".join(_parts)[:50000]

    # Guardrails tracked items — the things the guardrails coupling actually guards
    # in CLAUDE.md. If a CLAUDE.md edit touches none of these keywords it is prose:
    # the reconcile nudge cannot apply, so it is suppressed. settings.json is NEVER
    # gated. Edit this keyword set to match what your CLAUDE.md guardrails section
    # actually tracks.
    GUARD_KW = re.compile(
        r"boot\b|/(boot|handoff|audit|reflect|session)\b|"
        r"commands/|\bdeny\b|\ballow\b|Desktop|Downloads|"
        r"outbox|release\.py|scrub|egress|membrane|"
        r"Sonnet|Opus|Haiku|model-fit|model selection|model tier",
        re.IGNORECASE,
    )

    def guard_applies():
        # Only CLAUDE.md is diff-gated; settings.json (and anything else) always fires.
        if not p.endswith("/CLAUDE.md"):
            return True
        if not changed_known:
            return True  # fail open — never risk missing a real drift
        return bool(GUARD_KW.search(changed))

    hits = []

    def cat(label, pattern, msg, gate=None):
        # label is kept as the leading arg for readability/parity with the map;
        # it is no longer recorded to a machine log in the Core (audit reads the
        # markdown verdict logs instead — see audit.md guard-health).
        if re.search(pattern, p):
            if gate is not None and not gate():
                return
            hits.append(msg)

    # ── CONFIGURE: structural patterns + coupling messages ───────────────────────
    # Add one cat() call per structural file or group in your project.
    # label = short tag for the machine log; pattern = regex matching the path;
    # msg = what else must change when this file is edited.

    # Boot / handoff / audit loop
    cat("boot-loop", r"(/_LOADUP\.md|/_NEXT\.md|/boot\.md|/handoff\.md|/audit\.md|/reflect\.md|/session\.md|/next-write\.sh|/next-live\.sh|/next-consume\.sh|/next-boot\.sh)$",
        "Boot/handoff loop: parallel readers/writers must agree — boot output fields ↔ files actually loaded; "
        "the fast-path lives in _LOADUP §1 + boot.md always-load (keep aligned); "
        "the _NEXT 3-section format is a read/write contract (the cold-reader test + resolution-triggers must stay in sync across _NEXT.md / handoff.md).")
    # _LOADUP section pointers
    cat("loadup-ptrs", r"/_LOADUP\.md$",
        "Renumbering _LOADUP §N breaks every `§N` pointer in audit.md / boot.md / _NEXT.md / handoff.md.")
    # Schema / config (if your project carries templates or a config file)
    cat("schema-config", r"(/note\.md|/config\.yaml)$",
        "Schema/config: template field names ↔ any script that reads them ↔ _LOADUP reference section; "
        "config keys ↔ the code that loads them.")
    # Docs & narrative chain
    cat("docs-chain", r"(/SYSTEM_MAP\.md|/README\.md)",
        "Docs chain: rebuild downstream docs from the upstream canonical source, never a sibling; "
        "keep SYSTEM_MAP ↔ SYNC_MAP reconciled.")
    # Guardrails / control hub (diff-gated on CLAUDE.md via guard_applies)
    cat("guardrails", r"(/CLAUDE\.md|/settings\.json)$",
        "Guardrails: your edit touched a tracked item — reconcile it. boot-trigger phrases ↔ command "
        "files in ~/.claude/commands/; deny-fence ↔ boot always-load list; egress order; model-selection tiers. "
        "(On CLAUDE.md this nudge is suppressed for prose touching none of these — so if you see it, check which one moved.)",
        gate=guard_applies)
    # The map itself
    cat("map-self", r"/SYNC_MAP\.md$",
        "Editing the map itself — keep the SYSTEM_MAP cross-link in sync.")
    # The guard itself
    cat("guard-self", r"/drift-guard\.py$",
        "Editing the guard itself — if you changed the structural-path pattern list, "
        "section labels, WORKSPACE_ROOTS, or EXCLUDED_PREFIXES, also update SYNC_MAP.md "
        "so the map stays coherent with what the hook actually watches.")

    # ────────────────────────────────────────────────────────────────────────────

    if hits:
        emit("⚠ STRUCTURAL EDIT (" + path + ") — drift guard. Relevant SYNC_MAP couplings:\n- "
             + "\n- ".join(hits)
             + "\nAfter editing, grep -rn the tree for any renamed name/path/field/count before closing. "
               "Full map: SYNC_MAP.md")
    # else: silent — zero context cost on non-structural edits


if __name__ == "__main__":
    main()
