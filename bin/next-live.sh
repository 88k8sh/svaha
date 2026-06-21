#!/usr/bin/env bash
# next-live.sh <system-dir> [--check]
# The SINGLE SOURCE OF TRUTH for "which _NEXT sessions are live."
#
# WHY THIS EXISTS
# "List the active sessions" is easy to compute ad-hoc by eyeballing the next/
# folder — but that is both nondeterministic AND racy. With concurrent sessions,
# each one's /handoff `touch`es a _NEXT_NNN.consumed, so the live set mutates
# underneath any listing: a session can be retired by a parallel handoff mid-
# conversation, and a "live sessions" list rendered seconds later would silently
# drop it with no signal that it had just been consumed. From the user's seat an
# active session vanishes with no explanation.
#
# This script fixes that by being (a) deterministic — one defined rule, run as
# code, never eyeballed — and (b) race-aware — it surfaces sessions that were
# consumed in the recent window so a just-retired session is shown explicitly
# (with its consume time) instead of disappearing.
#
# ANY "list active / live sessions" request MUST run this script.
#
# Classification (per _NEXT_NNN.md):
#   LIVE-OPEN          no .consumed sidecar AND ## Next moves has real items
#   DONE-UNCONSUMED    no .consumed sidecar BUT ## Next moves is empty/"none"
#                      → limbo: the move finished but the stamp was never
#                        applied. Surfaced LOUDLY. Fix: touch the .consumed.
#   (consumed)         has .consumed sidecar → done, omitted from the live list,
#                      but listed under RECENTLY CONSUMED if stamped within the
#                      window (default 120 min; $NEXT_RECENT_MIN to override).
#   ORPHAN             .consumed sidecar with no matching _NEXT_NNN.md
#
# NOTE: a consumed file's frozen text still lists its original moves (the _NEXT
# files are never edited). So "consumed but text still lists open moves" is NOT
# a desync — it is the normal, expected state. We do not flag it.
#
# Modes:
#   (default)  live list + recently-consumed + any desync warnings
#   --check    print ONLY real desyncs (DONE-UNCONSUMED / ORPHAN); exit 1 if any
#
# Usage: next-live.sh <system-dir>
#        next-live.sh <system-dir> --check

set -uo pipefail

SYSTEM_DIR="${1:?Usage: next-live.sh <system-dir> [--check]}"
MODE="${2:-list}"
NEXT_DIR="${SYSTEM_DIR}/next"
RECENT_MIN="${NEXT_RECENT_MIN:-120}"

if [[ ! -d "${NEXT_DIR}" ]]; then
  echo "next-live.sh: '${NEXT_DIR}' not found — SYSTEM_DIR is not the system root." >&2
  exit 2
fi

# Does a file's `## Next moves` section contain a real move (numbered or
# bulleted line that is not just "none"/"n/a"/"done")?  0 = yes, 1 = no.
has_open_move() {
  awk '
    /^##[[:space:]]+[Nn]ext[[:space:]]+moves/ { insec=1; next }
    /^##[[:space:]]/                          { insec=0 }
    insec {
      line=$0; sub(/^[[:space:]]+/, "", line)
      if (line ~ /^[0-9]+\./ || line ~ /^-[[:space:]]/) {
        low=tolower(line)
        if (low !~ /^(-[[:space:]]*)?(none|n\/a|done)[[:space:]]*$/) found=1
      }
    }
    END { exit (found ? 0 : 1) }
  ' "$1"
}

# Best label for a file: the focus label from a "# _NEXT_NNN — label" title
# line, else the first real move text (title-less legacy files), trimmed.
label_for() {
  local f="$1" nnn="$2" h
  h=$(head -n 1 "$f")
  if [[ "$h" == "# _NEXT_${nnn} — "* ]]; then
    printf '%s' "${h#\# _NEXT_${nnn} — }"
    return
  fi
  # title-less: first real move line in ## Next moves
  awk '
    /^##[[:space:]]+[Nn]ext[[:space:]]+moves/ { insec=1; next }
    /^##[[:space:]]/                          { insec=0 }
    insec {
      line=$0; sub(/^[[:space:]]+/, "", line)
      if (line ~ /^[0-9]+\./) { sub(/^[0-9]+\.[[:space:]]*/, "", line);
                                print substr(line,1,70); exit }
    }
  ' "$f"
}

shopt -s nullglob
live_open=() ; done_unconsumed=() ; recent_consumed=() ; orphans=()

for f in "${NEXT_DIR}"/_NEXT_*.md; do
  base=$(basename "$f"); nnn=${base#_NEXT_}; nnn=${nnn%.md}
  if [[ -e "${NEXT_DIR}/_NEXT_${nnn}.consumed" ]]; then
    # consumed — surface only if stamped within the recent window
    if [[ -n "$(find "${NEXT_DIR}/_NEXT_${nnn}.consumed" -mmin "-${RECENT_MIN}" 2>/dev/null)" ]]; then
      ts=$(stat -f '%Sm' -t '%H:%M' "${NEXT_DIR}/_NEXT_${nnn}.consumed" 2>/dev/null \
           || date -r "${NEXT_DIR}/_NEXT_${nnn}.consumed" '+%H:%M' 2>/dev/null)
      recent_consumed+=("${nnn}|${ts}|$(label_for "$f" "$nnn")")
    fi
    continue
  fi
  if has_open_move "$f"; then
    live_open+=("${nnn}|$(label_for "$f" "$nnn")")
  else
    done_unconsumed+=("${nnn}|$(label_for "$f" "$nnn")")
  fi
done

for c in "${NEXT_DIR}"/_NEXT_*.consumed; do
  cb=$(basename "$c"); cn=${cb#_NEXT_}; cn=${cn%.consumed}
  [[ -e "${NEXT_DIR}/_NEXT_${cn}.md" ]] || orphans+=("$cn")
done
shopt -u nullglob

emit_desyncs() {   # returns 0 if any desync printed, else 1
  local any=1
  if (( ${#done_unconsumed[@]} )); then any=0
    echo "⚠ DONE-UNCONSUMED (move finished but never stamped — stamp these):"
    printf '%s\n' "${done_unconsumed[@]}" | sort | while IFS='|' read -r n l; do
      echo "  ${n} — ${l}   → touch next/_NEXT_${n}.consumed"
    done
  fi
  if (( ${#orphans[@]} )); then any=0
    echo "⚠ ORPHAN .consumed (sidecar with no _NEXT_NNN.md):"
    printf '  _NEXT_%s.consumed\n' "${orphans[@]}"
  fi
  return ${any}
}

if [[ "${MODE}" == "--check" ]]; then
  if emit_desyncs; then exit 1; fi
  echo "next-live: clean — every unconsumed _NEXT has open moves; no orphans."
  exit 0
fi

# ---- default list mode ----
if (( ${#live_open[@]} == 0 )); then
  echo "live sessions: none"
else
  echo "live sessions (${#live_open[@]}):"
  printf '%s\n' "${live_open[@]}" | sort | while IFS='|' read -r n l; do
    echo "  ${n} — ${l}"
  done
fi

if (( ${#recent_consumed[@]} )); then
  echo ""
  echo "recently consumed (last ${RECENT_MIN}m — retired by a handoff, possibly a concurrent session):"
  printf '%s\n' "${recent_consumed[@]}" | sort | while IFS='|' read -r n t l; do
    echo "  ${n} — ${l}   (consumed ${t})"
  done
fi

echo ""
emit_desyncs || true
