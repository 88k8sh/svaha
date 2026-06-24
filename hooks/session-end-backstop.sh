#!/usr/bin/env bash
# SessionEnd / PreCompact hook — the durability backstop.
#
# WHY THIS EXISTS: the auto-handoff loop is instruction-level — it lives in
# CLAUDE.md and depends on the model choosing to run /handoff on a wrap-up signal.
# The Stop hook (launchpad-nudge / resume-line-guard) nudges, but a session that
# is *killed* — a crash, a window close, or a context-wall /compact — never emits
# a clean Stop with the model still steering. In that path NOTHING carries the
# session forward: no _NEXT is minted, and the next boot starts cold. This hook is
# the event-driven catch: it fires once on SessionEnd (and on PreCompact, where
# supported), checks whether a _NEXT_NNN.md was written *this session*, and if not,
# tells the NEXT session to run /handoff or /reflect before it does anything else.
#
# Advisory / fail-soft by design: emits ONLY a systemMessage. It never blocks the
# session from ending and never forces an action — a wrong block here would strand
# the user mid-shutdown. Event-driven (fires on the lifecycle event, no polling).
#
# Reads the hook stdin JSON: { session_id, transcript_path, hook_event_name, ... }.
# SessionEnd may also carry { reason: "clear"|"logout"|"prompt_input_exit"|... }.

input=$(cat)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)
event=$(printf '%s' "$input" | jq -r '.hook_event_name // empty' 2>/dev/null)
reason=$(printf '%s' "$input" | jq -r '.reason // empty' 2>/dev/null)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)

# Resolve the project's system dir (per-project, self-discovered — no baked path),
# then use its next/. Bounded search around the session CWD, anchor _LOADUP.md:
#   1. up-scan: CWD + ancestors (covers launch inside the system or below it).
#   2. down-scan: CWD's immediate children, unambiguous match only (covers launch in a
#      workspace that *contains* the system — the nested layout).
#   3. last-ditch: the hook's own grandparent (in-kit combined-repo run).
# Never recursive. Fail-soft: if none yields a real next/ dir, we exit silent (see below).
base="${cwd:-$PWD}"
sysdir=""
d="$base"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  if [ -f "$d/_LOADUP.md" ]; then sysdir="$d"; break; fi
  d=$(dirname "$d")
done
[ -z "$sysdir" ] && [ -f "/_LOADUP.md" ] && sysdir="/"
if [ -z "$sysdir" ]; then
  # explicit dotfile skip (don't rely on ambient dotglob); dedup by real path (cd+pwd -P)
  # so a symlink twin counts once; newline-delimited so paths with spaces are safe.
  rps=""
  for c in "$base"/*/; do
    name=${c%/}; name=${name##*/}
    case "$name" in .*) continue;; esac
    [ -f "${c}_LOADUP.md" ] || continue
    rp=$(cd "${c%/}" 2>/dev/null && pwd -P) || continue
    rps="${rps}${rp}
"
  done
  if [ "$(printf '%s' "$rps" | sort -u | grep -c .)" -eq 1 ]; then
    sysdir=$(printf '%s' "$rps" | sort -u | grep -m1 .)
  fi
fi
nextdir=""
[ -n "$sysdir" ] && [ -d "${sysdir}/next" ] && nextdir="${sysdir}/next"
if [ -z "$nextdir" ]; then
  here=$(cd "$(dirname "$0")" 2>/dev/null && pwd)
  [ -d "${here}/../next" ] && nextdir=$(cd "${here}/../next" 2>/dev/null && pwd)
fi

# If we can't find the next/ dir, we can't tell whether a handoff was written —
# stay silent rather than nag with a false alarm (fail-soft).
if [ ! -d "$nextdir" ]; then exit 0; fi

# Was a _NEXT_NNN.md written or modified during THIS session?
# The session-start marker is dropped by the SessionStart wiring if present;
# absent that, fall back to a time window: any _NEXT file touched in the last
# 6 hours is treated as "this session's" handoff. The marker path is preferred.
start_marker="${TMPDIR:-/tmp}/claude-session-start-${sid}"

handoff_written=0
if [ -f "$start_marker" ]; then
  # Precise: anything in next/ newer than the session-start marker.
  newer=$(find "$nextdir" -name '_NEXT_*.md' -newer "$start_marker" 2>/dev/null | head -1)
  [ -n "$newer" ] && handoff_written=1
else
  # Fallback: any _NEXT file modified in the last 360 minutes.
  recent=$(find "$nextdir" -name '_NEXT_*.md' -mmin -360 2>/dev/null | head -1)
  [ -n "$recent" ] && handoff_written=1
fi

# A handoff was already minted this session — the loop closed cleanly. Silent.
if [ "$handoff_written" -eq 1 ]; then exit 0; fi

# Fire at most once per session per event-type (SessionEnd and PreCompact each
# get one shot — a PreCompact then a later SessionEnd is two distinct catches).
sentinel="${TMPDIR:-/tmp}/claude-sessionend-backstop-${sid}-${event:-x}"
if [ -f "$sentinel" ]; then exit 0; fi
touch "$sentinel" 2>/dev/null

# Some SessionEnd reasons are not real session ends we care about (e.g. a /clear
# that immediately restarts). Only nag on terminal-ish reasons; if reason is
# absent (PreCompact, or older CC), proceed — better to nudge than to drop work.
case "$reason" in
  clear)
    # /clear wipes context but the work may continue — skip the backstop.
    exit 0
    ;;
esac

if [ "$event" = "PreCompact" ]; then
  printf '{"systemMessage":"⚠ DURABILITY BACKSTOP (pre-compact) — context is about to be compacted and no _NEXT handoff was written this session. Before you lose the thread: run /handoff to mint a _NEXT_NNN.md (or /reflect if there is no in-flight work). Compaction will summarize, but a clean handoff is what the next boot reads."}\n'
else
  printf '{"systemMessage":"⚠ DURABILITY BACKSTOP (session-end) — this session is ending and no _NEXT handoff was written. The next session will start cold. On your very next turn (this or next session), run /handoff to mint a _NEXT_NNN.md, or /reflect if there was no in-flight work. Do not skip — this is the only thing carrying the session forward."}\n'
fi
exit 0
