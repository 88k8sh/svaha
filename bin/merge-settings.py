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


def merge_hooks(dst, src):
    # hooks: { EventName: [ {matcher?, hooks:[...]} , ... ] }
    # append the kit's per-event entries that aren't already present.
    for event, entries in src.items():
        union(dst.setdefault(event, []), entries)
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
