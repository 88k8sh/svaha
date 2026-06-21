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

    # ── CONFIGURE: scope strictly to this workspace — never fire on unrelated repos ──
    # Replace with your project root path(s). <system-dir> is your project root.
    WORKSPACE_ROOTS = [
        "<system-dir>/",    # ← CHANGE THIS to your project root (absolute path, e.g. "/Users/me/proj/")
        "/.claude/",
    ]
    if not any(root in p for root in WORKSPACE_ROOTS):
        sys.exit(0)

    # Sub-projects: skip files inside known non-live directories.
    # These share filenames with live plumbing but are not part of the running system
    # (e.g. starter packages, reference snapshots, archived copies).
    EXCLUDED_PREFIXES = [
        # "<system-dir>/context-mgmt-starter/",  # ← uncomment and add as needed
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
    cat("boot-loop", r"(/_LOADUP\.md|/_NEXT\.md|/boot\.md|/handoff\.md|/audit\.md|/reflect\.md|/session\.md|/next-write\.sh|/next-live\.sh)$",
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
