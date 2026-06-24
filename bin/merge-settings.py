#!/usr/bin/env python3
# merge-settings.py <source.json> <target.json>
#
# Safely merges Svaha's settings (source — the placeholder-substituted snippet)
# INTO the user's existing ~/.claude/settings.json (target), preserving every
# key already there. This is what lets setup.sh stop punting on an existing
# settings.json and just DO the merge — no hand-editing, no "inside or outside
# the brackets?" guesswork.
#
# Safety contract:
#   - Backs up the target (timestamped) BEFORE writing — the rollback path.
#   - Validates the merged result is real JSON before it replaces anything.
#   - Atomic write (tmp + os.replace) — never a half-written settings.json.
#   - Idempotent — re-running adds nothing already present (dedup by value).
#   - Never overrides a user's existing top-level key (theme, model, etc.);
#     only UNIONS the permission arrays and APPENDS missing hook entries.
#
# Exit non-zero on any failure (bad JSON in target, etc.) so setup.sh can fall
# back to the manual path with a clear message instead of corrupting anything.

import json, sys, os, shutil, datetime


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)        # raises on malformed JSON → caller handles


def _key(x):
    # stable identity for an arbitrary JSON value, for dedup
    return json.dumps(x, sort_keys=True)


def union(dst, src):
    """Append items from src not already in dst (by value); preserve dst order."""
    seen = {_key(x) for x in dst}
    for x in src:
        k = _key(x)
        if k not in seen:
            dst.append(x)
            seen.add(k)
    return dst


def merge_permissions(dst, src):
    # every value under "permissions" is an array (allow / ask / deny /
    # additionalDirectories) → union it; preserve any user key we don't ship.
    for key, val in src.items():
        if isinstance(val, list):
            dst[key] = union(dst.get(key, []), val)
        else:
            dst.setdefault(key, val)
    return dst


# Basenames of the scripts THIS kit ships + bakes an absolute path into. Used to
# recognize "our own" hook entries so a re-run after the kit MOVED (its baked path
# changed) — or any kit upgrade that changes a baked field (path, timeout,
# statusMessage) — REPLACES the stale entry instead of appending a duplicate that
# fires twice (and errors on every gated call if the old clone was deleted).
KIT_SCRIPT_BASENAMES = {
    "security-guard.py", "version-guard.py", "drift-guard.py", "coherence-check.py",
    "context-canary.sh", "launchpad-nudge.sh", "memory-reflect.sh",
    "resume-line-guard.sh", "session-end-backstop.sh", "session-start-marker.sh",
}


def _entry_kit_scripts(entry):
    """The set of kit script basenames an entry's hook commands reference. Empty →
    not one of ours (a user's own hook), so it is never touched."""
    found = set()
    if isinstance(entry, dict):
        for h in entry.get("hooks", []) or []:
            cmd = h.get("command", "") if isinstance(h, dict) else ""
            found |= {b for b in KIT_SCRIPT_BASENAMES if b in cmd}
    return found


def _entry_identity(entry):
    """Path-independent identity for one of our entries: (matcher, frozenset of kit
    scripts). A moved/upgraded kit entry matches its stale predecessor by this."""
    return (entry.get("matcher") if isinstance(entry, dict) else None,
            frozenset(_entry_kit_scripts(entry)))


def merge_hooks(dst, src):
    # hooks: { EventName: [ {matcher?, hooks:[...]} , ... ] }
    # For each source entry: if it is one of OURS (references a kit script), drop any
    # existing entry of the SAME identity (matcher + kit-script set) regardless of its
    # baked path, then append the fresh one — i.e. REPLACE, so re-running setup after a
    # move/upgrade never doubles a guard. Entries that aren't ours (a user's own hook,
    # even under the same event) are unioned by value and never clobbered. (Caveat: a
    # user hook hand-merged INTO one of our entry objects is replaced with it — keep
    # your own hooks in a separate entry, which is the normal layout.)
    for event, entries in src.items():
        dst_list = dst.setdefault(event, [])
        for s_entry in entries:
            if _entry_kit_scripts(s_entry):
                sid = _entry_identity(s_entry)
                dst_list[:] = [d for d in dst_list
                               if not (_entry_kit_scripts(d) and _entry_identity(d) == sid)]
                dst_list.append(s_entry)
            else:
                union(dst_list, [s_entry])
    return dst


def main():
    if len(sys.argv) != 3:
        print("usage: merge-settings.py <source.json> <target.json>", file=sys.stderr)
        return 2

    src_path, tgt_path = sys.argv[1], sys.argv[2]

    try:
        src = load(src_path)
    except (json.JSONDecodeError, OSError) as e:
        print(f"merge-settings: cannot read source '{src_path}': {e}", file=sys.stderr)
        return 1
    try:
        tgt = load(tgt_path)
    except json.JSONDecodeError as e:
        print(f"merge-settings: existing '{tgt_path}' is not valid JSON ({e}) — "
              f"not touching it; merge by hand.", file=sys.stderr)
        return 1

    # Backup BEFORE any write — this is the rollback path.
    backup = None
    if os.path.exists(tgt_path):
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = f"{tgt_path}.svaha-backup-{ts}"
        shutil.copy2(tgt_path, backup)

    if isinstance(src.get("permissions"), dict):
        tgt["permissions"] = merge_permissions(tgt.get("permissions", {}), src["permissions"])
    if isinstance(src.get("hooks"), dict):
        tgt["hooks"] = merge_hooks(tgt.get("hooks", {}), src["hooks"])
    # any other top-level key the kit ships: add only if the user lacks it
    for k, v in src.items():
        if k not in ("permissions", "hooks") and k not in tgt:
            tgt[k] = v

    out = json.dumps(tgt, indent=2) + "\n"
    json.loads(out)                     # final validation before we touch disk

    tmp = tgt_path + ".tmp"
    with open(tmp, "w") as f:
        f.write(out)
    os.replace(tmp, tgt_path)           # atomic

    msg = f"merged Svaha settings -> {tgt_path}"
    if backup:
        msg += f"  (backup: {os.path.basename(backup)})"
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
